from app.services.audit_service import add_data_source, add_event
from app.services.syndicated_data_service import (
    get_supported_symbol_count,
    get_syndicated_record,
    normalize_symbol,
    require_supported_symbol,
    search_symbols as search_syndicated_symbols,
    get_default_recommendation as get_syndicated_default_recommendation,
)
from app.utils.defaults import CSV_PROXY_SOURCE, LOOKUP_LIMIT


def get_market_record(symbol: str, audit: dict | None = None):
    record = get_syndicated_record(symbol)
    if audit is not None:
        add_data_source(audit, CSV_PROXY_SOURCE)
    if record is None:
        raise ValueError(f"Unsupported symbol '{normalize_symbol(symbol)}'. Use the CSV-backed lookup.")
    return type(
        "MarketRecord",
        (),
        {
            "symbol": record.symbol,
            "name": record.name,
            "asset_type": "stock" if record.asset_class.lower() == "stock" else record.asset_class.lower(),
            "sector_or_category": record.sector,
            "proxy_price": record.latest_price,
            "risk_bucket": "low" if record.portfolio_bucket in {"Core Bonds", "Short Treasury", "Inflation Shield"} else "high" if record.sector in {"Technology", "Communication Services", "Emerging Markets"} and record.asset_class.lower() == "stock" else "medium",
            "is_diversified": record.asset_class.lower() != "stock" or "Diversified" in record.portfolio_bucket,
        },
    )()


def validate_supported_symbol(symbol: str, audit: dict | None = None) -> str:
    normalized = require_supported_symbol(symbol)
    if audit is not None:
        add_data_source(audit, CSV_PROXY_SOURCE)
        add_event(audit, "audit_guardrail_agent", "validate_symbol", f"{normalized} is supported by the syndicated CSV dataset.")
    return normalized


def search_symbols(query: str, limit: int = LOOKUP_LIMIT, audit: dict | None = None) -> list[dict]:
    if audit is not None:
        add_data_source(audit, CSV_PROXY_SOURCE)
        add_event(audit, "market_dataset_service", "lookup", f"Lookup query '{query.strip().lower()}' searched against syndicated CSV dataset.")
    return search_syndicated_symbols(query, limit=limit)


def get_default_recommendation(candidates: list[str], exclude: set[str] | None = None, audit: dict | None = None):
    record = get_syndicated_default_recommendation(candidates, exclude=exclude)
    if audit is not None:
        add_data_source(audit, CSV_PROXY_SOURCE)
        add_event(audit, "market_context_agent", "select_candidate", f"Selected {record.symbol} as a diversified recommendation from the syndicated CSV dataset.")
    return record
