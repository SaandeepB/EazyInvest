def test_holdings_only_show_user_added_positions(client):
    initial = client.get("/holdings/")
    assert initial.status_code == 200
    assert initial.json()["holdings"] == []

    created = client.post("/holdings/", json={"symbol": "AAPL", "quantity": 10, "avg_cost": 150})
    assert created.status_code == 201
    assert created.json()["holding"]["symbol"] == "AAPL"

    listed = client.get("/holdings/")
    payload = listed.json()
    assert len(payload["holdings"]) == 1
    assert payload["holdings"][0]["symbol"] == "AAPL"
    assert payload["audit"]["feature"] == "holdings.list"


def test_unknown_symbol_is_allowed_and_estimated(client):
    response = client.post("/holdings/", json={"symbol": "NOTREAL", "quantity": 1, "avg_cost": 10})
    assert response.status_code == 201
    payload = response.json()["holding"]
    assert payload["symbol"] == "NOTREAL"
    assert payload["current_price"] is None
    assert payload["estimated_value"] == 10.0
