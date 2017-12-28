import pytest
from app.dashboard.render import (_insert_doc_handle,
                                  _normalize_product_title)


@pytest.mark.parametrize(
    'slug,expected_handle,expected_series_name',
    [('sqr-000', 'SQR-000', 'SQuaRE Technical Note'),
     ('dmtn-000', 'DMTN-000', 'Data Management Technical Note')])
def test_doc_handle(slug, expected_handle, expected_series_name):
    product = {
        'slug': slug,
    }

    _insert_doc_handle(product)
    assert product['doc_handle'] == expected_handle
    assert product['series_name'] == expected_series_name


@pytest.mark.parametrize(
    'title,expected_title',
    [('SQR-000: This is the real title',
      'This is the real title'),
     ('SQR-000: Starts with an S',
      'Starts with an S'),
     ('SQR-000 Starts with an S',
      'Starts with an S'),
     ('SQR-001 Starts with an S',
      'SQR-001 Starts with an S'),
     ('Starts with an S',
      'Starts with an S')])
def test_product_title(title, expected_title):
    product = {
        'doc_handle': 'SQR-000',
        'title': title
    }

    _normalize_product_title(product)
    assert product['title'] == expected_title
