"""Phase 1 regex extractor tests — pure Python, no SpaCy / API."""
from __future__ import annotations

import pytest

from phase1_spacy.rules import (
    find_invoice_date,
    find_invoice_number,
    find_line_items,
    find_total,
)


def test_invoice_number_various_formats():
    assert find_invoice_number("Invoice No: INV-2024-0042") == "INV-2024-0042"
    assert find_invoice_number("Invoice Number: HC-7781") == "HC-7781"
    assert find_invoice_number("Invoice # BTC/2024/0193") == "BTC/2024/0193"


def test_invoice_number_missing_returns_none():
    assert find_invoice_number("no invoice here") is None


@pytest.mark.parametrize("text, expected", [
    ("Date: 2024-04-08", "2024-04-08"),
    ("Dated: 22/05/2024", "2024-05-22"),
    ("Invoice Date: 12 March 2024", "2024-03-12"),
])
def test_invoice_date_parses_iso(text, expected):
    assert find_invoice_date(text) == expected


def test_invoice_date_missing_returns_none():
    assert find_invoice_date("no date in this string") is None


def test_total_with_explicit_currency():
    amount, currency = find_total("Total Amount: EUR 863.76")
    assert amount == 863.76
    assert currency == "EUR"


def test_total_without_currency_defaults_usd():
    amount, currency = find_total("Total: 1200")
    assert amount == 1200.0
    assert currency == "USD"


def test_total_strips_thousands_separator():
    amount, _ = find_total("Total Amount: USD 12,345.67")
    assert amount == 12345.67


def test_line_items_extraction_basic():
    text = """
Description                    Qty    Unit Price   Line Total
Stainless steel fasteners      120    0.45         54.00
Industrial PVC tubing 2m       40     3.20         128.00
"""
    items = find_line_items(text)
    assert len(items) == 2
    assert items[0]["quantity"] == 120.0
    assert items[0]["unit_price"] == 0.45
    assert items[0]["line_total"] == 54.0
    assert "fasteners" in items[0]["description"].lower()


def test_line_items_missing_returns_empty():
    assert find_line_items("just some prose without a table") == []
