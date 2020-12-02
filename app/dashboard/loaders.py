"""Dashboard build pipeline."""

import os
import json

import requests
from structlog import get_logger


def load_bulk_dashboard_data(product_url):
    bulk_url = "%s/dashboard" % product_url

    logger = get_logger("ltddasher")
    logger.info("Getting data from bulk endpoint", url=bulk_url)

    r = requests.get(bulk_url)
    r.raise_for_status()

    data = r.json()

    product_data = data['product']
    edition_data = {e['slug']: e for e in data['editions']}
    build_data = {b['slug']: b for b in data['builds']}

    logger.info("Finished getting data from bulk endpoint", url=bulk_url)

    return product_data, edition_data, build_data


def load_product_data(product_url):
    """Retrieve data about the product and its editions from the Keeper API.

    Parameters
    ----------
    product_url : `str`
        URL for the product's resource in the Keeper API (e.g.,
        `"https://keeper.lsst.codes/products/developer"`).

    Returns
    -------
    product_data : `dict`
        Dictionary with the product resource data.
    """
    # {
    #     "bucket_name": "lsst-the-docs",
    #     "doc_repo": "https://github.com/lsst-dm/dm_dev_guide.git",
    #     "domain": "developer.lsst.io",
    #     "fastly_domain": "n.global-ssl.fastly.net",
    #     "published_url": "https://developer.lsst.io",
    #     "root_domain": "lsst.io",
    #     "root_fastly_domain": "n.global-ssl.fastly.net",
    #     "self_url": "https://keeper.lsst.codes/products/developer",
    #     "slug": "developer",
    #     "title": "DM Developer Guide"
    # }
    logger = get_logger("ltddasher")
    logger = logger.debug('load_product_data')
    r = requests.get(product_url)
    return r.json()


def load_edition_data(product_url):
    r"""Retrieve all edition resources for a particular product from the
    Keeper API.

    Parameters
    ----------
    product_url : `str`
        URL for the product's resource in the Keeper API (e.g.,
        `"https://keeper.lsst.codes/products/developer"`).

    Returns
    -------
    edition_data : `dict`
        Dictionary keyed by edition slug, containing `dict`\ s of edition
        data.
    """
    logger = get_logger("ltddasher")
    logger = logger.debug('load_edition_data')

    edition_root_url = product_url + '/editions/'
    r = requests.get(edition_root_url)
    edition_urls = r.json()['editions']

    edition_data = {}
    for edition_url in edition_urls:
        # {
        #     "build_url": "https://keeper.lsst.codes/builds/1278",
        #     "date_created": "2017-01-27T20:43:55Z",
        #     "date_ended": null,
        #     "date_rebuilt": "2017-01-27T20:45:04Z",
        #     "product_url": "https://keeper.lsst.codes/products/developer",
        #     "published_url": "https://developer.lsst.io/v/DM-8995",
        #     "self_url": "https://keeper.lsst.codes/editions/327",
        #     "slug": "DM-8995",
        #     "surrogate_key": "1482f52465e34e3da958edbfcaf6de35",
        #     "title": "DM-8995",
        #     "tracked_refs": [
        #         "tickets/DM-8995"
        #     ]
        # }
        r = requests.get(edition_url)
        edition_object = r.json()
        edition_data[edition_object['slug']] = edition_object
    return edition_data


def load_build_data(product_url):
    logger = get_logger("ltddasher")
    logger = logger.debug('load_build_data')

    build_root_url = product_url + '/builds/'
    r = requests.get(build_root_url)
    build_urls = r.json()['builds']

    build_data = {}
    for build_url in build_urls:
        r = requests.get(build_url)
        build_object = r.json()
        build_data[build_object['slug']] = build_object

    return build_data


def _cache_path(cache_dir, product_slug, dataset_type):
    assert dataset_type in ('product', 'editions', 'builds')
    name = '{product}_{dataset_type}'.format(product=product_slug,
                                             dataset_type=dataset_type)
    cache_path = os.path.join(cache_dir, name) + '.json'
    return cache_path


def cache_data_for_dev(json_data, cache_dir, product_slug, dataset_type):
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
    cache_path = _cache_path(cache_dir, product_slug, dataset_type)
    with open(cache_path, 'w') as f:
        json.dump(json_data, f, indent=2, sort_keys=True)


def load_dataset_with_caching(cache_dir, product_slug, dataset_type):
    cache_path = _cache_path(cache_dir, product_slug, dataset_type)
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f, encoding='utf-8')
    except OSError:
        # Can't find cached data, so reload it
        product_url = 'https://keeper.lsst.codes/products/{slug}'.format(
            slug=product_slug)
        if dataset_type == 'product':
            cache_data = load_product_data(product_url)
        elif dataset_type == 'editions':
            cache_data = load_edition_data(product_url)
        elif dataset_type == 'builds':
            cache_data = load_build_data(product_url)
        else:
            raise RuntimeError(
                'Unknown dataset_type: {0}'.format(dataset_type))
        cache_data_for_dev(cache_data, cache_dir, product_slug, dataset_type)
    return cache_data
