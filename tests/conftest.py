"""py.test fixtures available to all test modules without explicit import."""

import pytest

from app import create_app
from app.testutils import TestClient


@pytest.fixture
def empty_app(request):
    """An application with only a single user, but otherwise empty"""
    app = create_app(profile='testing')
    ctx = app.app_context()
    ctx.push()

    def fin():
        ctx.pop()

    request.addfinalizer(fin)
    return app


@pytest.fixture
def anon_client(empty_app):
    """Anonymous client."""
    client = TestClient(empty_app)
    return client
