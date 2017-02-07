"""Worker functions to handle dashboard builds."""

from .loaders import load_product_data, load_edition_data, load_build_data
from .render import render_edition_dashboard, render_build_dashboard


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
    # Get data from the Keeper API
    product_data = load_product_data(product_url)
    edition_data = load_edition_data(product_url)
    build_data = load_build_data(product_url)

    # Turn data into HTML dashboars for editions and builds
    edition_html_data = render_edition_dashboard(product_data, edition_data)
    build_html_data = render_build_dashboard(product_data, build_data)

    # Upload static assets
    upload_static_assets(product_data, config)

    # Upload dashboards
    upload_html_data(edition_html_data,
                     'v/index.html',
                     product_data,
                     config)
    upload_html_data(build_html_data,
                     'builds/index.html',
                     product_data,
                     config)


def upload_static_assets(product_data, config):
    """Upload all static assets included in ``app/assets/manifest.yaml`` to S3.

    Parameters
    ----------
    product_data : `dict`
        Dataset describing the product resource from Keeper's
        ``/products/(slug)`` endpoint.
    config : `flask.config`
        Flask configuration.

    Notes
    -----
    The YAML manifest file is designed to ensure that compiled static assets
    are included in the application container, since they are not embedded in
    Git in their compiled form.
    """
    pass


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
    pass
