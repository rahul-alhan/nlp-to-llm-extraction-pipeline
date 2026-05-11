"""Shared Pydantic schema for extracted invoice data."""
from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field, field_validator


class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    line_total: float


class SupplierInvoice(BaseModel):
    supplier_name: str
    invoice_number: str
    invoice_date: date
    total_amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=3, max_length=3)
    line_items: list[LineItem] = []

    @field_validator("currency")
    @classmethod
    def upper_currency(cls, v: str) -> str:
        return v.upper()
