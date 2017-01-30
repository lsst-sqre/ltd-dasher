"""Test app.routes.healthz."""


def test_healthz(anon_client):
    r = anon_client.get('/healthz')
    assert r.status == 200
