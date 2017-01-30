"""Dashboard build pipeline."""

import requests


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
    r = requests.get(product_url)
    return r.json()


def load_edition_data(product_url):
    """Retrieve all edition resources for a particular product from the
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
    build_root_url = product_url + '/builds/'
    r = requests.get(build_root_url)
    build_urls = r.json()['builds']

    build_data = {}
    for build_url in build_urls:
        r = requests.get(build_url)
        build_object = r.json()
        build_data[build_object['slug']] = build_object

    return build_data
