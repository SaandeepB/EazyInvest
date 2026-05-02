def test_navn_holding_uses_requested_csv_price(client):
    response = client.post("/holdings/", json={"symbol": "NAVN", "quantity": 10, "avg_cost": 14})
    assert response.status_code == 201
    holding = response.json()["holding"]
    assert holding["current_price"] == 18.0
    assert holding["cost_basis"] == 140.0
    assert holding["current_value"] == 180.0


def test_aapl_and_testxyz_holdings_show_market_vs_estimated_values(client):
    aapl = client.post("/holdings/", json={"symbol": "AAPL", "quantity": 2, "avg_cost": 150}).json()["holding"]
    testxyz = client.post("/holdings/", json={"symbol": "TESTXYZ", "quantity": 2, "avg_cost": 15}).json()["holding"]
    assert aapl["current_price"] == 189.5
    assert aapl["current_value"] == 379.0
    assert aapl["estimated_value"] is None
    assert testxyz["current_price"] is None
    assert testxyz["current_value"] is None
    assert testxyz["estimated_value"] == 30.0
