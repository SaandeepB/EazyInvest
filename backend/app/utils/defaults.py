APP_NAME = "EazyInvest"
PRIMARY_USER_ID = 1
SYNDICATED_PRICE_SOURCE = "syndicated_csv"
CSV_PROXY_SOURCE = SYNDICATED_PRICE_SOURCE
LOOKUP_LIMIT = 8
CONCENTRATION_THRESHOLD_PCT = 30.0

DEFAULT_USER_PROFILE = {
    "name": "EazyInvest User",
    "risk_profile": "Balanced",
    "goal": "Long-term growth",
    "time_horizon": "10+ years",
    "planned_withdrawal_pct": 0.0,
    "starting_amount": 0.0,
    "monthly_contribution": 0.0,
    "contribution_stability": "Stable",
    "behavioral_risk": "Hold",
    "has_emergency_fund": "Yes",
    "account_type": "Taxable",
    "has_external_holdings": "No",
    "ux_mode": "Simple",
}

SCENARIO_CATALOG = [
    {
        "type": "market_drop",
        "label": "Market drops 20%",
        "description": "Stress test stock-heavy portfolios against a broad drawdown.",
    },
    {
        "type": "inflation",
        "label": "Inflation stays high",
        "description": "Check concentration in rate-sensitive growth and diversify exposure.",
    },
    {
        "type": "withdrawal",
        "label": "Need cash next year",
        "description": "Create a more stable bucket for near-term spending needs.",
    },
    {
        "type": "reduce_risk",
        "label": "Retire / reduce risk soon",
        "description": "Reduce stock concentration toward the user's target risk mix.",
    },
    {
        "type": "concentration",
        "label": "One holding is too big",
        "description": "Trim overweight positions and spread exposure more evenly.",
    },
]

DEFAULT_DIVERSIFIERS = {
    "equity": ["VTI", "VOO", "VT", "SCHD"],
    "defensive": ["BND", "AGG", "BIL", "SHV"],
    "inflation": ["VTI", "SCHD", "TIP", "XLE"],
}
