from app.services.market_dataset_service import get_market_record, get_supported_symbol_count, search_symbols


def test_market_proxy_loads_supported_universe():
    assert get_supported_symbol_count() >= 100
    record = get_market_record("aapl")
    assert record.symbol == "AAPL"
    assert record.proxy_price > 0


def test_symbol_lookup_returns_ranked_matches():
    results = search_symbols("vt")
    symbols = [item["symbol"] for item in results]
    assert "VTI" in symbols or "VT" in symbols
