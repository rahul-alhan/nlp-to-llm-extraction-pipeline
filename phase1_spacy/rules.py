"""Regex-based field extractors — phase 1."""
from __future__ import annotations

import re
from datetime import datetime

INVOICE_NUM = re.compile(r"Invoice\s*(?:No\.?|Number|#)\s*[:\-]?\s*([A-Z0-9\-]+)", re.I)
DATE_PATTERNS = [
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    re.compile(r"\b(\d{2}/\d{2}/\d{4})\b"),
    re.compile(r"\b(\d{1,2}\s+[A-Za-z]+\s+\d{4})\b"),
]
TOTAL = re.compile(r"Total\s*(?:Amount)?\s*[:\-]?\s*([A-Z]{3})?\s*([0-9,]+(?:\.\d{2})?)", re.I)
LINE_ITEM = re.compile(
    r"^\s*(?P<desc>.+?)\s{2,}(?P<qty>\d+(?:\.\d+)?)\s+(?P<price>\d+(?:\.\d+)?)\s+(?P<total>\d+(?:\.\d+)?)\s*$",
    re.M,
)


def find_invoice_number(text: str) -> str | None:
    m = INVOICE_NUM.search(text)
    return m.group(1) if m else None


def find_invoice_date(text: str) -> str | None:
    for pat in DATE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        raw = m.group(1)
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d %B %Y", "%d %b %Y"):
            try:
                return datetime.strptime(raw, fmt).date().isoformat()
            except ValueError:
                continue
    return None


def find_total(text: str) -> tuple[float | None, str | None]:
    m = TOTAL.search(text)
    if not m:
        return None, None
    currency = (m.group(1) or "USD").upper()
    amount = float(m.group(2).replace(",", ""))
    return amount, currency


def find_line_items(text: str) -> list[dict]:
    items = []
    for m in LINE_ITEM.finditer(text):
        items.append(
            {
                "description": m.group("desc").strip(),
                "quantity": float(m.group("qty")),
                "unit_price": float(m.group("price")),
                "line_total": float(m.group("total")),
            }
        )
    return items
