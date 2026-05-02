from types import SimpleNamespace

from app.services.profile_target_service import profiler_output_from_answers


def test_beginner_high_risk_maps_to_watchlist_profile():
    answers = SimpleNamespace(
        goal="Build wealth",
        time_horizon="10+ years",
        starting_amount=500,
        monthly_contribution=100,
        contribution_stability="Stable",
        loss_comfort="Fine with it",
        behavioral_risk="Buy more",
        near_term_withdrawal=False,
        withdrawal_pct=0.0,
        has_emergency_fund="Yes",
        account_type="Taxable",
        has_external_holdings="No",
        ux_mode="Control",
    )
    profile = profiler_output_from_answers(answers, custom_scenario_text="I like taking risks and tracking watchlist names.")
    assert profile["investor_segment"] == "High-Risk Watchlist User"
    assert profile["risk_profile"] == "Growth"
    assert profile["recommended_scenario_type"] == "market_drop"


def test_need_cash_next_year_maps_to_withdrawal_profile():
    answers = SimpleNamespace(
        goal="Home down payment",
        time_horizon="1-2 years",
        starting_amount=10000,
        monthly_contribution=300,
        contribution_stability="Stable",
        loss_comfort="Cautious",
        behavioral_risk="Hold",
        near_term_withdrawal=True,
        withdrawal_pct=20.0,
        has_emergency_fund="Yes",
        account_type="Taxable",
        has_external_holdings="No",
        ux_mode="Simple",
    )
    profile = profiler_output_from_answers(answers, custom_scenario_text="I need cash next year.")
    assert profile["investor_segment"] == "Goal-Focused Planner"
    assert profile["liquidity_need"] == "high"
    assert profile["recommended_scenario_type"] == "withdrawal"


def test_balanced_long_term_investor_maps_to_builder():
    answers = SimpleNamespace(
        goal="Retirement",
        time_horizon="10+ years",
        starting_amount=25000,
        monthly_contribution=500,
        contribution_stability="Stable",
        loss_comfort="Cautious",
        behavioral_risk="Hold",
        near_term_withdrawal=False,
        withdrawal_pct=0.0,
        has_emergency_fund="Yes",
        account_type="401k",
        has_external_holdings="No",
        ux_mode="Simple",
    )
    profile = profiler_output_from_answers(answers)
    assert profile["investor_segment"] == "Balanced Builder"
    assert profile["risk_profile"] == "Balanced"
    assert profile["time_horizon_bucket"] == "long_term"
