from app.config.target_profiles import TARGET_PROFILE_CATEGORIES
from app.services.audit_service import add_event


LIQUIDITY_SYMBOLS = {"BIL", "SHV", "SGOV"}
INTERNATIONAL_SYMBOLS = {"VXUS", "VEA", "VWO", "IXUS", "IEFA"}
DIVIDEND_SYMBOLS = {"SCHD", "VYM", "DGRO", "HDV"}
DEFENSIVE_SYMBOLS = {"BND", "AGG", "TIP"}
THEMATIC_SYMBOLS = {"QQQ", "ARKK", "XLE", "XLK", "SMH", "SOXX"}
DEFENSIVE_BUCKETS = {"Core Bonds", "Short Treasury", "Inflation Shield"}


def order_actions(actions: list[dict], audit: dict | None = None) -> list[dict]:
    ordered = sorted(
        actions,
        key=lambda item: (0 if item["action"] == "trim" else 1 if item["action"] == "add" else 2, -abs(item["change_pct"])),
    )
    if audit is not None:
        add_event(audit, "rebalancing_agent", "order_actions", f"Ordered {len(ordered)} actions for presentation.")
    return ordered


def build_allocation_view(holdings: list[dict], audit: dict | None = None) -> dict[str, float]:
    allocation = {category: 0.0 for category in TARGET_PROFILE_CATEGORIES}
    for holding in holdings:
        category = classify_target_category(holding)
        allocation[category] = round(allocation[category] + holding["weight_pct"], 2)

    if audit is not None:
        add_event(audit, "rebalancing_agent", "allocation_view", "Built allocation view across dense target-profile categories.")
    return allocation


def compare_to_target_profile(current_allocation: dict[str, float], target_allocation: dict[str, float], audit: dict | None = None) -> list[dict]:
    drift = []
    for category in TARGET_PROFILE_CATEGORIES:
        current = round(current_allocation.get(category, 0.0), 2)
        target = round(target_allocation.get(category, 0.0), 2)
        drift.append(
            {
                "category": category,
                "current_pct": current,
                "target_pct": target,
                "drift_pct": round(current - target, 2),
            }
        )
    ordered = sorted(drift, key=lambda item: abs(item["drift_pct"]), reverse=True)
    if audit is not None:
        add_event(audit, "rebalancing_agent", "compare_target", f"Compared current allocation against {len(target_allocation)} target categories.")
    return ordered


def classify_target_category(holding: dict) -> str:
    symbol = holding["symbol"].upper()
    asset_type = holding.get("asset_type", "").lower()
    portfolio_bucket = holding.get("portfolio_bucket", "")
    sector = holding.get("sector_or_category", "")
    name = holding.get("name", "").lower()
    is_diversified = holding.get("is_diversified", False)

    if symbol in LIQUIDITY_SYMBOLS:
        return "Liquidity Placeholder"
    if asset_type == "stock":
        return "Individual Stocks"
    if symbol in DIVIDEND_SYMBOLS or "dividend" in name or "income" in name:
        return "Dividend / Income Funds"
    if symbol in INTERNATIONAL_SYMBOLS or "international" in portfolio_bucket.lower() or "international" in sector.lower():
        return "International Funds"
    if symbol in DEFENSIVE_SYMBOLS or portfolio_bucket in DEFENSIVE_BUCKETS or any(term in sector.lower() for term in ("bond", "treasury", "inflation")):
        return "Defensive / Stability Funds"
    if symbol in THEMATIC_SYMBOLS or (asset_type != "stock" and not is_diversified):
        return "Thematic / Sector Exposure"
    return "Broad Market Funds"
