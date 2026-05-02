def test_portfolio_summary_uses_syndicated_csv_and_audit(client):
    client.post(
        "/users/onboarding",
        json={
            "goal": "Retirement savings",
            "time_horizon": "10+ years",
            "starting_amount": 1000,
            "monthly_contribution": 250,
            "contribution_stability": "Stable",
            "loss_comfort": "Fine with it",
            "behavioral_risk": "Hold",
            "near_term_withdrawal": False,
            "withdrawal_pct": 0,
            "has_emergency_fund": "Yes",
            "account_type": "Taxable",
            "has_external_holdings": "No",
            "ux_mode": "Simple",
        },
    )
    client.post("/holdings/", json={"symbol": "AAPL", "quantity": 10, "avg_cost": 150})
    response = client.get("/portfolio/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["portfolio"]["price_source"] == "syndicated_csv"
    assert payload["portfolio"]["data_source_note"] == "Latest available market proxy"
    assert payload["portfolio"]["allocation_bars"]
    assert payload["portfolio"]["top_holdings"][0]["symbol"] == "AAPL"
    assert payload["market_context"]["source"] == "syndicated_csv"
    assert payload["audit"]["checks"][0]["name"] == "no_live_market_api"


def test_portfolio_summary_updates_after_adding_holdings(client):
    before = client.get("/portfolio/summary")
    assert before.status_code == 200
    before_payload = before.json()
    assert before_payload["portfolio"]["total_value"] == 0.0
    assert before_payload["portfolio"]["holdings_count"] == 0

    client.post("/holdings/", json={"symbol": "NAVN", "quantity": 10, "avg_cost": 14})
    after = client.get("/portfolio/summary")
    assert after.status_code == 200

    after_payload = after.json()
    assert after_payload["portfolio"]["total_value"] == 180.0
    assert after_payload["portfolio"]["total_cost"] == 140.0
    assert after_payload["portfolio"]["top_holding_symbol"] == "NAVN"
    assert after_payload["portfolio"]["top_holdings"][0]["symbol"] == "NAVN"
    assert after_payload["portfolio"]["allocation_bars"][0]["label"] == "US Growth"
