from typing import Any

from app.services.syndicated_data_service import get_syndicated_record, normalize_symbol


MISSING_NAME = "Unmapped symbol"
MISSING_ASSET_TYPE = "unknown"
MISSING_BUCKET = "Unclassified"
MISSING_SECTOR = "Unknown"
MISSING_PRICE_SOURCE = "missing_from_syndicated_csv"
MISSING_PRICE_FRESHNESS = "estimated_from_avg_cost"
LIVE_PRICE_FRESHNESS = "end_of_day_snapshot"


def enrich_holding(symbol: str, quantity: float, avg_cost: float, **extra: Any) -> dict[str, Any]:
    normalized = normalize_symbol(symbol)
    cost_basis = round(quantity * avg_cost, 2)
    record = get_syndicated_record(normalized)

    if record is None:
        enriched = {
            "symbol": normalized,
            "name": extra.get("name") or MISSING_NAME,
            "asset_type": MISSING_ASSET_TYPE,
            "portfolio_bucket": MISSING_BUCKET,
            "sector_or_category": MISSING_SECTOR,
            "quantity": quantity,
            "avg_cost": round(avg_cost, 2),
            "cost_basis": cost_basis,
            "current_price": None,
            "current_value": None,
            "estimated_value": cost_basis,
            "price_source": MISSING_PRICE_SOURCE,
            "price_freshness": MISSING_PRICE_FRESHNESS,
            "as_of_date": None,
            "risk_bucket": "unknown",
            "is_diversified": False,
        }
    else:
        current_price = round(record.latest_price, 2)
        current_value = round(current_price * quantity, 2)
        estimated_value = None
        asset_type = "stock" if record.asset_class.lower() == "stock" else record.asset_class.lower()
        enriched = {
            "symbol": record.symbol,
            "name": record.name,
            "asset_type": asset_type,
            "portfolio_bucket": record.portfolio_bucket,
            "sector_or_category": record.sector,
            "quantity": quantity,
            "avg_cost": round(avg_cost, 2),
            "cost_basis": cost_basis,
            "current_price": current_price,
            "current_value": current_value,
            "estimated_value": estimated_value,
            "price_source": record.source,
            "price_freshness": LIVE_PRICE_FRESHNESS,
            "as_of_date": record.as_of_date,
            "risk_bucket": _risk_bucket(record.asset_class, record.portfolio_bucket, record.sector),
            "is_diversified": _is_diversified(record.asset_class, record.portfolio_bucket),
        }

    effective_value = enriched["current_value"] if enriched["current_value"] is not None else enriched["estimated_value"]
    gain_loss = round(effective_value - cost_basis, 2) if effective_value is not None else 0.0
    gain_loss_pct = round((gain_loss / cost_basis) * 100, 2) if cost_basis > 0 else 0.0

    enriched.update(
        {
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
            "effective_value": round(effective_value, 2) if effective_value is not None else 0.0,
            **extra,
        }
    )
    return enriched


def enrich_holdings(holdings: list[Any]) -> list[dict[str, Any]]:
    enriched_records: list[dict[str, Any]] = []
    for holding in holdings:
        enriched = enrich_holding(
            symbol=holding.symbol,
            quantity=holding.quantity,
            avg_cost=holding.avg_cost,
            id=getattr(holding, "id", None),
            updated_at=getattr(holding, "updated_at", None),
        )
        enriched_records.append(enriched)

    total_value = sum(item["effective_value"] for item in enriched_records) or 1.0
    for item in enriched_records:
        item["weight_pct"] = round(item["effective_value"] / total_value * 100, 2)
    return sorted(enriched_records, key=lambda item: item["effective_value"], reverse=True)


def build_simulated_holdings(after_allocation: dict[str, float], total_value: float) -> list[dict[str, Any]]:
    simulated: list[dict[str, Any]] = []
    for symbol, weight in after_allocation.items():
        record = get_syndicated_record(symbol)
        if record is None:
            continue
        current_value = round(total_value * weight / 100, 2)
        quantity = round(current_value / record.latest_price, 6) if record.latest_price else 0.0
        simulated.append(
            enrich_holding(
                symbol=record.symbol,
                quantity=quantity,
                avg_cost=record.latest_price,
                weight_pct=round(weight, 2),
                current_value=current_value,
                effective_value=current_value,
            )
        )
        simulated[-1]["weight_pct"] = round(weight, 2)
        simulated[-1]["current_value"] = current_value
        simulated[-1]["estimated_value"] = None
        simulated[-1]["effective_value"] = current_value
    return sorted(simulated, key=lambda item: item["effective_value"], reverse=True)


def _is_diversified(asset_class: str, portfolio_bucket: str) -> bool:
    return asset_class.lower() != "stock" or "Diversified" in portfolio_bucket


def _risk_bucket(asset_class: str, portfolio_bucket: str, sector: str) -> str:
    if asset_class.lower() != "stock" and portfolio_bucket in {"Core Bonds", "Short Treasury", "Inflation Shield"}:
        return "low"
    if sector in {"Technology", "Communication Services", "Emerging Markets"} and asset_class.lower() == "stock":
        return "high"
    return "medium"
