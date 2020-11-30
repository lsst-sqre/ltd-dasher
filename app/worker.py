"""Worker functions to handle dashboard builds."""

import os

import boto3
from structlog import get_logger
from requests.exceptions import HTTPError
from ltdconveyor import (upload_dir, upload_object,
                         create_dir_redirect_object, purge_key)

from .dashboard.loaders import (load_product_data, load_edition_data,
                                load_build_data, load_bulk_dashboard_data)
from .dashboard.render import (render_edition_dashboard,
                               render_build_dashboard)


def build_dashboard_for_product(product_url, config):
    """"Build the dashboard for a single (direct)

    This function is called directly by the API route.

    Parameters
    ----------
    product_url : `str`
        URL of the product resource in the Keeper API.
    product_data : `dict`
        Dataset describing the product resource from Keeper's
        ``/products/(slug)`` endpoint.
    config : `flask.config`
        Flask configuration.
    """
    logger = get_logger()
    logger.debug('build_dashboard_for_product', product_url=product_url)

    # Sanity check that configs exist
    assert config['AWS_ID'] is not None
    assert config['AWS_SECRET'] is not None
    assert config['FASTLY_KEY'] is not None
    assert config['FASTLY_SERVICE_ID'] is not None

    # Get data from the Keeper API
    try:
        product_data, edition_data, build_data = load_bulk_dashboard_data(
            product_url
        )
    except HTTPError:
        product_data = load_product_data(product_url)
        edition_data = load_edition_data(product_url)
        build_data = load_build_data(product_url)

    # absolute URL for asset directory
    asset_dir = product_data['published_url'] + '/_dasher-assets'

    # Turn data into HTML dashboards for editions and builds
    logger.debug("rendering edition_html_data")
    edition_html_data = render_edition_dashboard(
        product_data, edition_data, asset_dir=asset_dir)
    logger.debug("rendering build_html_data")
    build_html_data = render_build_dashboard(
        product_data, build_data, asset_dir=asset_dir)

    # Upload static assets
    upload_static_assets(product_data, config)

    # Upload dashboards
    if config['TESTING'] is False:
        # FIXME really want to mock these instead of flagging
        upload_html_data(edition_html_data,
                         'v/index.html',
                         product_data,
                         config)
        upload_html_data(build_html_data,
                         'builds/index.html',
                         product_data,
                         config)

    # Purge fastly cache
    if config['TESTING'] is False:
        # FIXME really want to mock this instead of flagging
        purge_key(product_data['surrogate_key'],
                  config['FASTLY_SERVICE_ID'],
                  config['FASTLY_KEY'])
        logger.info("Fastly purge_key",
                    surrogate_key=product_data['surrogate_key'])


def upload_static_assets(product_data, config):
    """Upload all static assets included in ``app/assets`` to S3.

    Parameters
    ----------
    product_data : `dict`
        Dataset describing the product resource from Keeper's
        ``/products/(slug)`` endpoint.
    config : `flask.config`
        Flask configuration.

    Notes
    -----
    The contents of ``app/assets`` are not commited in Git since they are
    compiled by the Gulp workflow. It would be good to script the Docker
    image build process to ensure that asserts and compiled and installed.
    """
    logger = get_logger()
    logger.debug("upload_static_assets")

    # local filesystem path
    package_assets_dir = os.path.join(os.path.dirname(__file__),
                                      'dashboard', 'assets')
    logger.debug(package_assets_dir=package_assets_dir)

    # path to the assets directory in the bucket
    bucket_path_prefix = os.path.join(product_data['slug'], '_dasher-assets')

    if config['TESTING'] is False:
        # css may not necessarily be built in test environment;
        # see http://ls.st/tac
        assert os.path.isdir(package_assets_dir)

        # FIXME really want to mock upload_dir instead of flagging it
        logger.debug(assets_bucket_path_prefix=bucket_path_prefix)
        upload_dir(product_data['bucket_name'],
                   bucket_path_prefix,
                   package_assets_dir,
                   upload_dir_redirect_objects=True,
                   surrogate_key=product_data['surrogate_key'],
                   surrogate_control='max-age=31536000',
                   cache_control='no-cache',
                   acl='public-read',
                   aws_access_key_id=config['AWS_ID'],
                   aws_secret_access_key=config['AWS_SECRET'])


def upload_html_data(html_data, relative_path, product_data, config):
    """Upload all static assets included in ``app/assets/manifest.yaml`` to S3.

    Parameters
    ----------
    html_data : `str`
        The page's HTML data.
    relative_path : `str`
        Path of this page, relative to the product's root prefix.
    product_data : `dict`
        Dataset describing the product resource from Keeper's
        ``/products/(slug)`` endpoint.
    config : `flask.config`
        Flask configuration.
    """
    logger = get_logger()
    logger.debug('upload_html_data', upload_path=relative_path)

    surrogate_key = product_data['surrogate_key']

    if not relative_path.startswith('/'):
        relative_path = '/' + relative_path
    bucket_path = product_data['slug'] + relative_path

    product_data['bucket_name']

    session = boto3.session.Session(
        aws_access_key_id=config['AWS_ID'],
        aws_secret_access_key=config['AWS_SECRET'])
    s3 = session.resource('s3')
    bucket = s3.Bucket(product_data['bucket_name'])

    # Have Fastly cache the dashboard for a year (or until purged)
    metadata = {'surrogate-key': surrogate_key,
                'surrogate-control': 'max-age=31536000'}
    acl = 'public-read'
    # Have the *browser* never cache the dashboard
    cache_control = 'no-cache'

    # Upload HTML object
    upload_object(bucket_path,
                  bucket,
                  content=html_data,
                  metadata=metadata,
                  acl=acl,
                  cache_control=cache_control,
                  content_type='text/html')

    # Upload directory redirect object
    bucket_dir_path = os.path.dirname(bucket_path)
    create_dir_redirect_object(bucket_dir_path, bucket,
                               metadata=metadata,
                               acl=acl,
                               cache_control=cache_control)
