from collections import defaultdict

from app.models.models import Holding, User
from app.services.portfolio_math_service import compute_health, enrich_holdings
from app.utils.defaults import CONCENTRATION_THRESHOLD_PCT, CSV_PROXY_SOURCE


DATA_SOURCE_NOTE = "Latest available market proxy"


def build_portfolio_summary(holdings: list[Holding], user: User, audit: dict | None = None) -> dict:
    enriched_holdings = enrich_holdings(holdings, audit)
    return _build_portfolio_payload(enriched_holdings, user)


def _build_portfolio_payload(enriched_holdings: list[dict], user: User) -> dict:
    if not enriched_holdings:
        health = compute_health([], user)
        return {
            "total_value": 0.0,
            "total_cost": 0.0,
            "total_gain_loss": 0.0,
            "total_gain_loss_pct": 0.0,
            "stock_value": 0.0,
            "etf_value": 0.0,
            "stock_allocation_pct": 0.0,
            "etf_allocation_pct": 0.0,
            "holdings_count": 0,
            "top_holding_symbol": "",
            "top_holding_pct": 0.0,
            "concentration_warning": False,
            "health": health,
            "risk_level": "Unknown",
            "price_source": CSV_PROXY_SOURCE,
            "data_source_note": DATA_SOURCE_NOTE,
            "allocation_bars": [],
            "top_holdings": [],
            "holdings": [],
        }

    total_value = round(sum(item["effective_value"] for item in enriched_holdings), 2)
    total_cost = round(sum(item["cost_basis"] for item in enriched_holdings), 2)
    total_gain_loss = round(total_value - total_cost, 2)
    total_gain_loss_pct = round((total_gain_loss / total_cost * 100) if total_cost else 0.0, 2)
    stock_value = round(sum(item["effective_value"] for item in enriched_holdings if item["asset_type"] == "stock"), 2)
    etf_value = round(sum(item["effective_value"] for item in enriched_holdings if item["asset_type"] != "stock"), 2)
    stock_allocation_pct = round(stock_value / total_value * 100, 2) if total_value else 0.0
    etf_allocation_pct = round(etf_value / total_value * 100, 2) if total_value else 0.0
    top_holding = enriched_holdings[0]
    concentration_warning = top_holding["weight_pct"] > CONCENTRATION_THRESHOLD_PCT
    health = compute_health(enriched_holdings, user)

    if stock_allocation_pct > 75 or top_holding["weight_pct"] > 35:
        risk_level = "High"
    elif stock_allocation_pct > 50 or top_holding["weight_pct"] > 25:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    holdings_view = [_to_allocation_item(item) for item in enriched_holdings]

    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain_loss": total_gain_loss,
        "total_gain_loss_pct": total_gain_loss_pct,
        "stock_value": stock_value,
        "etf_value": etf_value,
        "stock_allocation_pct": stock_allocation_pct,
        "etf_allocation_pct": etf_allocation_pct,
        "holdings_count": len(enriched_holdings),
        "top_holding_symbol": top_holding["symbol"],
        "top_holding_pct": round(top_holding["weight_pct"], 2),
        "concentration_warning": concentration_warning,
        "health": health,
        "risk_level": risk_level,
        "price_source": CSV_PROXY_SOURCE,
        "data_source_note": DATA_SOURCE_NOTE,
        "allocation_bars": _build_allocation_bars(enriched_holdings, total_value),
        "top_holdings": holdings_view[:5],
        "holdings": holdings_view,
    }


def _build_allocation_bars(enriched_holdings: list[dict], total_value: float) -> list[dict]:
    grouped_values: dict[str, float] = defaultdict(float)
    for item in enriched_holdings:
        grouped_values[item["portfolio_bucket"]] += item["effective_value"]

    bars = [
        {
            "label": label,
            "value": round(value, 2),
            "weight_pct": round((value / total_value) * 100, 2) if total_value else 0.0,
        }
        for label, value in grouped_values.items()
    ]
    return sorted(bars, key=lambda item: item["value"], reverse=True)


def _to_allocation_item(item: dict) -> dict:
    return {
        "symbol": item["symbol"],
        "name": item["name"],
        "asset_type": item["asset_type"],
        "sector_or_category": item["sector_or_category"],
        "current_value": item["effective_value"],
        "weight_pct": item["weight_pct"],
        "gain_loss": item["gain_loss"],
        "gain_loss_pct": item["gain_loss_pct"],
    }
