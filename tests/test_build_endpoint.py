"""Test app.routes.build."""


def test_rebuild_dashboards(anon_client):
    """Test dashboard rebuilds with full client."""
    r = anon_client.post('/build', {})
    assert r.status == 202
