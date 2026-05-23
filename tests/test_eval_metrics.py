"""Eval metric smoke tests — pure logic, no models."""
from __future__ import annotations

from eval.metrics import KEY_FIELDS, field_accuracy


def test_parse_error_counts_zero_correct():
    truth = {"supplier_name": "Acme", "invoice_number": "1", "invoice_date": "2024-01-01",
             "total_amount": 100.0, "currency": "USD"}
    r = field_accuracy({"_parse_error": True}, truth)
    assert r["correct"] == 0
    assert r["parsed"] is False


def test_exact_field_match_counts():
    truth = {"supplier_name": "Acme", "invoice_number": "X1", "invoice_date": "2024-01-01",
             "total_amount": 100.0, "currency": "USD"}
    pred = dict(truth)
    r = field_accuracy(pred, truth)
    assert r["correct"] == len(KEY_FIELDS)
    assert r["parsed"] is True


def test_supplier_match_is_case_insensitive():
    truth = {"supplier_name": "ACME"}
    pred = {"supplier_name": " acme "}
    r = field_accuracy(pred, truth)
    assert r["correct"] == 1


def test_line_item_count_is_scored_when_truth_provided():
    truth = {"n_line_items": 3}
    pred = {"line_items": [{}, {}, {}]}
    r = field_accuracy(pred, truth)
    assert r["correct"] == 1


def test_line_item_count_mismatch_does_not_score():
    truth = {"n_line_items": 3}
    pred = {"line_items": [{}, {}]}
    r = field_accuracy(pred, truth)
    assert r["correct"] == 0
