"""Field-level accuracy + JSON parse rate metrics."""
from __future__ import annotations


KEY_FIELDS = ["supplier_name", "invoice_number", "invoice_date", "total_amount", "currency"]


def field_accuracy(predicted: dict, truth: dict) -> dict:
    if predicted.get("_parse_error"):
        return {"correct": 0, "total": len(KEY_FIELDS), "parsed": False}
    correct = 0
    for f in KEY_FIELDS:
        p = predicted.get(f)
        t = truth.get(f)
        if isinstance(p, str) and isinstance(t, str):
            if p.strip().lower() == t.strip().lower():
                correct += 1
        elif p == t:
            correct += 1
    n_truth = truth.get("n_line_items")
    if n_truth is not None:
        n_pred = len(predicted.get("line_items", []) or [])
        if n_pred == n_truth:
            correct += 1
    return {"correct": correct, "total": len(KEY_FIELDS) + (1 if n_truth is not None else 0), "parsed": True}
