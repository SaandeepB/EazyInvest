from app.services.valuation_service import enrich_holding


def test_valuation_service_uses_csv_price_when_symbol_exists():
    enriched = enrich_holding(symbol="NAVN", quantity=4, avg_cost=20)
    assert enriched["symbol"] == "NAVN"
    assert enriched["current_price"] == 18.0
    assert enriched["current_value"] == 72.0
    assert enriched["estimated_value"] is None
    assert enriched["price_source"] == "syndicated_csv"


def test_valuation_service_falls_back_to_estimated_value_when_symbol_missing():
    enriched = enrich_holding(symbol="TESTXYZ", quantity=3, avg_cost=12.5)
    assert enriched["current_price"] is None
    assert enriched["current_value"] is None
    assert enriched["estimated_value"] == 37.5
    assert enriched["price_source"] == "missing_from_syndicated_csv"
