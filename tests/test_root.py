"""Test app.routes.root."""

import app


def test_root_endpoint(anon_client):
    """Test dashboard rebuilds with full client."""
    r = anon_client.get('/')
    assert r.status == 200
    assert r.json['dasher_version'] == app.__version__
