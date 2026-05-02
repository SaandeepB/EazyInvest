from collections import defaultdict

from app.services.audit_service import add_event
from app.services.market_dataset_service import get_supported_symbol_count
from app.utils.defaults import CSV_PROXY_SOURCE


def build_market_context(enriched_holdings: list[dict], audit: dict | None = None) -> dict:
    sector_weights: dict[str, float] = defaultdict(float)
    diversified_weight = 0.0
    for holding in enriched_holdings:
        sector_weights[holding["sector_or_category"]] += holding["weight_pct"]
        if holding["is_diversified"]:
            diversified_weight += holding["weight_pct"]

    top_sectors = [sector for sector, _ in sorted(sector_weights.items(), key=lambda item: item[1], reverse=True)[:3]]
    if not top_sectors:
        top_sectors = ["No holdings yet"]

    narrative = (
        f"EazyInvest is using the syndicated CSV dataset for all market context. "
        f"Your top sector exposures are {', '.join(top_sectors)} and {diversified_weight:.1f}% of the portfolio sits in diversified instruments."
        if enriched_holdings
        else "EazyInvest is using the syndicated CSV dataset. Add holdings to see sector and diversification context."
    )
    if audit is not None:
        add_event(audit, "market_context_agent", "summarize_context", narrative)
    return {
        "source": CSV_PROXY_SOURCE,
        "supported_symbol_count": get_supported_symbol_count(),
        "top_sectors": top_sectors,
        "diversified_weight_pct": round(diversified_weight, 2),
        "narrative": narrative,
    }


def build_scenario_market_context(
    enriched_holdings: list[dict],
    scenario_type: str,
    profiler_output: dict | None = None,
    audit: dict | None = None,
) -> dict:
    context = build_market_context(enriched_holdings, audit=None)
    if not enriched_holdings:
        return context

    stock_weight = round(sum(item["weight_pct"] for item in enriched_holdings if item["asset_type"] == "stock"), 2)
    top_sector = context["top_sectors"][0]
    target_name = profiler_output["target_profile_name"] if profiler_output else "current profile"

    scenario_note_map = {
        "market_drop": f"Stock-heavy exposure is about {stock_weight:.1f}% and {top_sector} is the top sector to watch in a drawdown.",
        "inflation": f"{top_sector} is the largest sector, so inflation sensitivity is checked against that concentration first.",
        "withdrawal": f"Near-term liquidity planning focuses on the current {stock_weight:.1f}% stock weight and the need for a steadier sleeve.",
        "reduce_risk": f"The scenario compares the current mix with the {target_name} allocation targets before suggesting trims.",
        "concentration": f"The concentration check starts with the largest sector, {top_sector}, and the biggest position weights.",
    }
    context["narrative"] = scenario_note_map.get(scenario_type, context["narrative"])
    if audit is not None:
        add_event(audit, "market_context_agent", "scenario_context", context["narrative"])
    return context
