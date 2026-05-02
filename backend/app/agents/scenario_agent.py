import re

from app.services.audit_service import add_event
from app.utils.defaults import SCENARIO_CATALOG


CATALOG_MAP = {item["type"]: item for item in SCENARIO_CATALOG}
SCENARIO_PRIORITY = ["withdrawal", "reduce_risk", "concentration", "inflation", "market_drop"]


def list_scenarios(audit: dict | None = None) -> list[dict]:
    if audit is not None:
        add_event(audit, "scenario_agent", "catalog", "Returned deterministic scenario planner catalog.")
    return SCENARIO_CATALOG


def validate_scenario_request(scenario_type: str, custom_params: dict | None, audit: dict | None = None) -> dict:
    if scenario_type not in CATALOG_MAP:
        raise ValueError(f"Unsupported scenario '{scenario_type}'.")
    params = custom_params or {}
    if "withdrawal_pct" in params and float(params["withdrawal_pct"]) < 0:
        raise ValueError("withdrawal_pct must be non-negative.")
    if "threshold" in params and float(params["threshold"]) <= 0:
        raise ValueError("threshold must be greater than zero.")
    if "drop_pct" in params and float(params["drop_pct"]) <= 0:
        raise ValueError("drop_pct must be greater than zero.")
    if audit is not None:
        add_event(audit, "scenario_agent", "validate", f"Validated scenario request for {scenario_type}.")
    return CATALOG_MAP[scenario_type]


def resolve_scenario_request(
    scenario_type: str | None,
    custom_scenario_text: str | None,
    custom_params: dict | None,
    profiler_output: dict | None,
    audit: dict | None = None,
) -> dict:
    text = (custom_scenario_text or "").strip()
    params = dict(custom_params or {})
    concerns = classify_custom_concerns(text)

    if scenario_type:
        scenario_meta = validate_scenario_request(scenario_type, params, audit)
        resolved_type = scenario_type
    elif text:
        fallback = profiler_output["recommended_scenario_type"] if profiler_output else "reduce_risk"
        resolved_type = concerns[0] if concerns else fallback
        scenario_meta = validate_scenario_request(resolved_type, params, audit)
    else:
        raise ValueError("Provide either a scenario_type or custom_scenario_text.")

    extracted_params = extract_custom_params(text, resolved_type)
    for key, value in extracted_params.items():
        params.setdefault(key, value)
    validate_scenario_request(resolved_type, params, audit)

    if audit is not None:
        detail = f"Resolved scenario request to {resolved_type}"
        if concerns:
            detail += f" from concerns {', '.join(concerns)}"
        add_event(audit, "scenario_agent", "route", detail + ".")

    return {
        "scenario_type": resolved_type,
        "scenario_meta": scenario_meta,
        "custom_params": params,
        "concerns": concerns,
    }


def classify_custom_concerns(text: str) -> list[str]:
    normalized = text.lower()
    detected: set[str] = set()

    if any(keyword in normalized for keyword in ("cash", "withdraw", "need money", "next year", "liquidity", "spending")):
        detected.add("withdrawal")
    if any(keyword in normalized for keyword in ("retire", "retirement", "reduce risk", "de-risk", "safer", "less risk", "soon")):
        detected.add("reduce_risk")
    if any(keyword in normalized for keyword in ("too big", "overweight", "concentrat", "single stock", "dominate")):
        detected.add("concentration")
    if any(keyword in normalized for keyword in ("inflation", "prices", "rates", "cost of living")):
        detected.add("inflation")
    if any(keyword in normalized for keyword in ("drop", "crash", "drawdown", "bear market", "selloff")):
        detected.add("market_drop")

    return [scenario for scenario in SCENARIO_PRIORITY if scenario in detected]


def extract_custom_params(text: str, scenario_type: str) -> dict:
    if not text:
        return {}

    percentages = [float(match) for match in re.findall(r"(\d+(?:\.\d+)?)\s*%", text.lower())]
    params: dict[str, float] = {}

    if scenario_type == "withdrawal":
        if percentages:
            params["withdrawal_pct"] = percentages[0]
    elif scenario_type == "market_drop":
        if percentages:
            params["drop_pct"] = percentages[-1]
    elif scenario_type == "concentration":
        if percentages:
            params["threshold"] = percentages[0]
    return params
