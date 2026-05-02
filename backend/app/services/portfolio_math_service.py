from app.models.models import Holding
from app.services.valuation_service import (
    build_simulated_holdings as build_simulated_holdings_core,
    enrich_holdings as enrich_holdings_core,
)
from app.utils.defaults import CONCENTRATION_THRESHOLD_PCT, CSV_PROXY_SOURCE


def enrich_holdings(holdings: list[Holding], audit: dict | None = None) -> list[dict]:
    _ = audit
    return enrich_holdings_core(holdings)


def compute_health(enriched_holdings: list[dict], user) -> dict:
    if not enriched_holdings:
        return {
            "overall": 0.0,
            "diversification": 0.0,
            "concentration": 100.0,
            "risk_alignment": 50.0,
            "liquidity_readiness": 50.0,
            "label": "No holdings",
        }

    holdings_count = len(enriched_holdings)
    unique_sectors = len({item["sector_or_category"] for item in enriched_holdings})
    diversification = min(100.0, holdings_count / 8 * 60 + unique_sectors / 6 * 40)

    top_weight = max(item["weight_pct"] for item in enriched_holdings)
    if top_weight > 45:
        concentration = 25.0
    elif top_weight > 35:
        concentration = 50.0
    elif top_weight > CONCENTRATION_THRESHOLD_PCT:
        concentration = 70.0
    else:
        concentration = 92.0

    stock_pct = sum(item["weight_pct"] for item in enriched_holdings if item["asset_type"] == "stock")
    target_stock_pct = {"Conservative": 35.0, "Balanced": 55.0, "Growth": 75.0}.get(getattr(user, "risk_profile", "Balanced"), 55.0)
    risk_alignment = max(0.0, 100.0 - abs(stock_pct - target_stock_pct) * 2.2)

    diversified_pct = sum(item["weight_pct"] for item in enriched_holdings if item["is_diversified"])
    liquidity_readiness = min(100.0, 35.0 + diversified_pct * 0.65)
    if getattr(user, "planned_withdrawal_pct", 0.0) > 20:
        liquidity_readiness = max(liquidity_readiness, 60.0)

    overall = diversification * 0.3 + concentration * 0.3 + risk_alignment * 0.25 + liquidity_readiness * 0.15
    if overall >= 75:
        label = "Good"
    elif overall >= 50:
        label = "Fair"
    else:
        label = "Needs Attention"

    return {
        "overall": round(overall, 1),
        "diversification": round(diversification, 1),
        "concentration": round(concentration, 1),
        "risk_alignment": round(risk_alignment, 1),
        "liquidity_readiness": round(liquidity_readiness, 1),
        "label": label,
    }


def compute_portfolio_payload(enriched_holdings: list[dict], user) -> dict:
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
            "holdings": [],
        }

    total_value = round(sum(item["effective_value"] for item in enriched_holdings), 2)
    total_cost = round(sum(item["avg_cost"] * item["quantity"] for item in enriched_holdings), 2)
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
        "holdings": [
            {
                "symbol": item["symbol"],
                "name": item["name"],
                "asset_type": item["asset_type"],
                "sector_or_category": item["sector_or_category"],
                "current_value": item["effective_value"],
                "weight_pct": item["weight_pct"],
                "gain_loss": item["gain_loss"],
                "gain_loss_pct": item["gain_loss_pct"],
            }
            for item in enriched_holdings
        ],
    }


def build_simulated_holdings(after_allocation: dict[str, float], total_value: float, audit: dict | None = None) -> list[dict]:
    _ = audit
    return build_simulated_holdings_core(after_allocation, total_value)
