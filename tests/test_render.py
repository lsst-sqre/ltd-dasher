from app.dashboard.render import _insert_doc_handle


def test_doc_handle():
    product = {
        'slug': 'sqr-000',
        'title': 'SQR-000: This is the real title'
    }

    _insert_doc_handle(product)
    assert product['title'] == 'This is the real title'
    assert product['doc_handle'] == 'SQR-000'


def test_no_handle():
    product = {
        'slug': 'developer',
        'title': 'DM Developer Guide'
    }

    _insert_doc_handle(product)
    assert product['title'] == 'DM Developer Guide'
    assert 'doc_handle' not in product
