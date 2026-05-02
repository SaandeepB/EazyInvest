def test_scenario_response_includes_audit_result(client):
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
    response = client.post(
        "/scenarios/analyze",
        json={"custom_scenario_text": "I might need 20% of my money next year and I am worried the market may drop."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"]["audit_result"]["overall_status"] in {"Pass", "Review Needed", "Fail"}
    assert len(payload["scenario"]["audit_result"]["controls"]) == 12


def test_audit_demo_endpoints_return_pass_review_fail_examples(client):
    results = client.get("/audit/demo-results")
    assert results.status_code == 200
    payload = results.json()
    statuses = {item["audit_result"]["overall_status"] for item in payload["results"]}
    assert statuses == {"Pass", "Review Needed", "Fail"}

    logs = client.get("/audit/demo-logs")
    assert logs.status_code == 200
    assert len(logs.json()["logs"]) == 3
