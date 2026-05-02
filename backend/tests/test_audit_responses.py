def test_lookup_and_delete_include_audit(client):
    lookup = client.get("/holdings/lookup?q=app")
    assert lookup.status_code == 200
    assert "audit" in lookup.json()

    created = client.post("/holdings/", json={"symbol": "AAPL", "quantity": 1, "avg_cost": 150}).json()
    holding_id = created["holding"]["id"]
    deleted = client.delete(f"/holdings/{holding_id}")
    assert deleted.status_code == 200
    assert deleted.json()["audit"]["feature"] == "holdings.delete"
