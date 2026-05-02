import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.utils.defaults import LOOKUP_LIMIT, SYNDICATED_PRICE_SOURCE


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "syndicated_prices.csv"


@dataclass(frozen=True)
class SyndicatedPriceRecord:
    symbol: str
    name: str
    asset_class: str
    portfolio_bucket: str
    sector: str
    latest_price: float
    previous_close: float
    as_of_date: str
    source: str


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


@lru_cache(maxsize=1)
def load_syndicated_prices() -> dict[str, SyndicatedPriceRecord]:
    records: dict[str, SyndicatedPriceRecord] = {}
    with DATA_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            record = SyndicatedPriceRecord(
                symbol=normalize_symbol(row["symbol"]),
                name=row["name"].strip(),
                asset_class=row["asset_class"].strip(),
                portfolio_bucket=row["portfolio_bucket"].strip(),
                sector=row["sector"].strip(),
                latest_price=float(row["latest_price"]),
                previous_close=float(row["previous_close"]),
                as_of_date=row["as_of_date"].strip(),
                source=row["source"].strip() or SYNDICATED_PRICE_SOURCE,
            )
            records[record.symbol] = record
    return records


def get_supported_symbol_count() -> int:
    return len(load_syndicated_prices())


def get_syndicated_record(symbol: str) -> SyndicatedPriceRecord | None:
    return load_syndicated_prices().get(normalize_symbol(symbol))


def require_supported_symbol(symbol: str) -> str:
    normalized = normalize_symbol(symbol)
    if get_syndicated_record(normalized) is None:
        raise ValueError(f"Unsupported symbol '{normalized}'. Use the syndicated CSV lookup.")
    return normalized


def search_symbols(query: str, limit: int = LOOKUP_LIMIT) -> list[dict]:
    text = query.strip().lower()
    if not text:
        return []

    starts_with: list[dict] = []
    contains: list[dict] = []
    for record in load_syndicated_prices().values():
        haystack = f"{record.symbol} {record.name}".lower()
        item = {
            "symbol": record.symbol,
            "name": record.name,
            "asset_class": record.asset_class,
            "portfolio_bucket": record.portfolio_bucket,
            "sector": record.sector,
            "latest_price": round(record.latest_price, 2),
            "as_of_date": record.as_of_date,
            "source": record.source,
            # compatibility fields for the current routes/frontend
            "asset_type": _asset_type_from_class(record.asset_class),
            "sector_or_category": record.sector,
            "proxy_price": round(record.latest_price, 2),
            "risk_bucket": _risk_bucket_from_record(record),
            "is_diversified": _is_diversified(record),
        }
        if record.symbol.lower().startswith(text) or record.name.lower().startswith(text):
            starts_with.append(item)
        elif text in haystack:
            contains.append(item)
    return (starts_with + contains)[:limit]


def get_default_recommendation(candidates: list[str], exclude: set[str] | None = None):
    exclude = exclude or set()
    for symbol in candidates:
        if normalize_symbol(symbol) in exclude:
            continue
        record = get_syndicated_record(symbol)
        if record is not None:
            return record
    raise ValueError("No recommendation candidate found in the syndicated CSV dataset.")


def _asset_type_from_class(asset_class: str) -> str:
    return "stock" if asset_class.lower() == "stock" else asset_class.lower()


def _is_diversified(record: SyndicatedPriceRecord) -> bool:
    diversified_classes = {"etf", "bond_etf", "index_fund", "international_etf", "bond"}
    return record.asset_class.lower() in diversified_classes or "Diversified" in record.portfolio_bucket


def _risk_bucket_from_record(record: SyndicatedPriceRecord) -> str:
    low_buckets = {"Core Bonds", "Short Treasury", "Inflation Shield"}
    high_sectors = {"Technology", "Communication Services", "Emerging Markets"}
    if record.portfolio_bucket in low_buckets:
        return "low"
    if record.sector in high_sectors and record.asset_class.lower() == "stock":
        return "high"
    return "medium"
