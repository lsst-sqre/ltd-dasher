"""Filters for Jinja2 templates."""

__all__ = ['filter_simple_date']


def filter_simple_date(value):
    """Filter a `datetime.datetime` into a 'YYYY-MM-DD' string."""
    return value.strftime('%Y-%m-%d')
