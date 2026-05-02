def test_scenario_analysis_returns_audit_and_projection(client):
    client.post("/holdings/", json={"symbol": "AAPL", "quantity": 10, "avg_cost": 150})
    client.post("/holdings/", json={"symbol": "MSFT", "quantity": 5, "avg_cost": 300})
    response = client.post("/scenarios/analyze", json={"scenario_type": "market_drop", "custom_params": {}})
    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"]["scenario_type"] == "market_drop"
    assert "audit" in payload
    assert "after_allocation" in payload["scenario"]
    assert "current_allocation" in payload["scenario"]
    assert "market_context" in payload["scenario"]


def test_empty_portfolio_scenario_is_safe(client):
    response = client.post("/scenarios/analyze", json={"scenario_type": "reduce_risk", "custom_params": {}})
    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"]["actions"] == []


def test_custom_scenario_text_routes_deterministically(client):
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
    client.post("/holdings/", json={"symbol": "MSFT", "quantity": 5, "avg_cost": 300})
    response = client.post(
        "/scenarios/analyze",
        json={
            "custom_scenario_text": "I might need 20% of my money next year and I am worried the market may drop."
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"]["scenario_type"] == "withdrawal"
    assert payload["scenario"]["profiler_output"]["recommended_scenario_type"] == "withdrawal"
    assert payload["scenario"]["market_context"]["source"] == "syndicated_csv"
    assert "market_drop" in payload["scenario"]["summary"]
