def _svc(client, name="api"):
    r = client.post("/api/v1/services", json={"name": name, "url": "https://example.com"})
    assert r.status_code == 201
    return r.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_service_crud(client):
    s = _svc(client)
    assert client.get(f"/api/v1/services/{s['id']}").status_code == 200
    assert len(client.get("/api/v1/services").json()) == 1
    assert client.delete(f"/api/v1/services/{s['id']}").status_code == 204
    assert client.get(f"/api/v1/services/{s['id']}").status_code == 404


def test_duplicate_service_rejected(client):
    _svc(client)
    r = client.post("/api/v1/services", json={"name": "api", "url": "https://example.com"})
    assert r.status_code == 409


def test_metric_for_unknown_service(client):
    r = client.post("/api/v1/metrics", json={"service_id": "00000000-0000-0000-0000-000000000000", "name": "cpu", "value": 1})
    assert r.status_code == 404


def test_alert_fires_on_threshold(client):
    s = _svc(client)
    client.post("/api/v1/alerts/rules", json={"service_id": s["id"], "metric": "cpu", "comparator": "gt", "threshold": 90})
    r = client.post("/api/v1/metrics", json={"service_id": s["id"], "name": "cpu", "value": 95})
    assert r.json()["alerts_fired"] == 1
    r = client.post("/api/v1/metrics", json={"service_id": s["id"], "name": "cpu", "value": 50})
    assert r.json()["alerts_fired"] == 0
    assert len(client.get("/api/v1/alerts").json()) == 1
    assert len(client.get(f"/api/v1/metrics/{s['id']}?name=cpu").json()) == 2
