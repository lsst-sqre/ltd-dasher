"""Test app.routes.build."""

import responses


mock_product_data = {
    "bucket_name": "lsst-the-docs",
    "doc_repo": "https://github.com/lsst-sqre/test-059.git",
    "domain": "test-059.lsst.io",
    "fastly_domain": "n.global-ssl.fastly.net",
    "published_url": "https://test-059.lsst.io",
    "root_domain": "lsst.io",
    "root_fastly_domain": "n.global-ssl.fastly.net",
    "self_url": "https://keeper-staging.lsst.codes/products/test-059",
    "slug": "test-059",
    "surrogate_key": "235becbe0b8349aa88b7f6e086529d77",
    "title": "Test Technote Via Bot"
}

mock_editions_data = {
    "editions": [
        "https://keeper-staging.lsst.codes/editions/388",
        "https://keeper-staging.lsst.codes/editions/390"
    ]
}

mock_edition_388_data = {
    "build_url": "https://keeper-staging.lsst.codes/builds/1322",
    "date_created": "2017-02-03T23:49:23Z",
    "date_ended": None,
    "date_rebuilt": "2017-02-03T23:51:21Z",
    "product_url": "https://keeper-staging.lsst.codes/products/test-059",
    "published_url": "https://test-059.lsst.io",
    "self_url": "https://keeper-staging.lsst.codes/editions/388",
    "slug": "main",
    "surrogate_key": "c1e29b6b1c97450c9d6d854ee3395ec9",
    "title": "Latest",
    "tracked_refs": [
        "master"
    ]
}

mock_edition_390_data = {
    "build_url": "https://keeper-staging.lsst.codes/builds/1324",
    "date_created": "2017-02-09T23:40:57Z",
    "date_ended": None,
    "date_rebuilt": "2017-02-09T23:41:17Z",
    "product_url": "https://keeper-staging.lsst.codes/products/test-059",
    "published_url": "https://test-059.lsst.io/v/test-branch",
    "self_url": "https://keeper-staging.lsst.codes/editions/390",
    "slug": "test-branch",
    "surrogate_key": "99ab3d93b1b54a4ea49dbe1764b7ea6a",
    "title": "test-branch",
    "tracked_refs": [
        "test-branch"
    ]
}

mock_builds_data = {
    "builds": [
        "https://keeper-staging.lsst.codes/builds/1322",
        "https://keeper-staging.lsst.codes/builds/1324"
    ]
}

mock_build_1322_data = {
    "bucket_name": "lsst-the-docs",
    "bucket_root_dir": "test-059/builds/1",
    "date_created": "2017-02-03T23:51:08Z",
    "date_ended": None,
    "git_refs": [
        "master"
    ],
    "github_requester": None,
    "product_url": "https://keeper-staging.lsst.codes/products/test-059",
    "published_url": "https://test-059.lsst.io/builds/1",
    "self_url": "https://keeper-staging.lsst.codes/builds/1322",
    "slug": "1",
    "surrogate_key": "006e34ec8f714aed956292645bb7e432",
    "uploaded": True
}

mock_build_1324_data = {
    "bucket_name": "lsst-the-docs",
    "bucket_root_dir": "test-059/builds/2",
    "date_created": "2017-02-09T23:40:57Z",
    "date_ended": None,
    "git_refs": [
        "test-branch"
    ],
    "github_requester": None,
    "product_url": "https://keeper-staging.lsst.codes/products/test-059",
    "published_url": "https://test-059.lsst.io/builds/2",
    "self_url": "https://keeper-staging.lsst.codes/builds/1324",
    "slug": "2",
    "surrogate_key": "a7dc0f6b0f4b40cdab851ff68be0ee51",
    "uploaded": True
}


@responses.activate
def test_rebuild_dashboards(anon_client):
    """Test dashboard rebuilds with full client."""
    responses.add(
        responses.GET,
        'https://keeper-staging.lsst.codes/products/test-059',
        json=mock_product_data,
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://keeper-staging.lsst.codes/products/test-059/editions/',
        json=mock_editions_data,
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://keeper-staging.lsst.codes/editions/388',
        json=mock_edition_388_data,
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://keeper-staging.lsst.codes/editions/390',
        json=mock_edition_390_data,
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://keeper-staging.lsst.codes/products/test-059/builds/',
        json=mock_builds_data,
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://keeper-staging.lsst.codes/builds/1322',
        json=mock_build_1322_data,
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        'https://keeper-staging.lsst.codes/builds/1324',
        json=mock_build_1324_data,
        status=200,
        content_type='application/json')

    r = anon_client.post(
        '/build',
        {
            'product_urls': ['https://keeper-staging.lsst.codes/'
                             'products/test-059']
        }
    )
    assert r.status == 202
