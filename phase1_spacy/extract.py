"""Phase 1 — SpaCy NER + regex extractor."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import spacy
from spacy.matcher import Matcher

from . import rules
from .ner_patterns import SUPPLIER_PATTERNS

_NLP = None


def _nlp():
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def find_supplier(text: str) -> str | None:
    nlp = _nlp()
    doc = nlp(text)
    matcher = Matcher(nlp.vocab)
    for i, p in enumerate(SUPPLIER_PATTERNS):
        matcher.add(f"SUPPLIER_{i}", [p])
    matches = matcher(doc)
    if matches:
        _, start, end = matches[0]
        return doc[start:end].text.strip()
    for ent in doc.ents:
        if ent.label_ == "ORG":
            return ent.text.strip()
    return None


def extract(text: str) -> dict:
    amount, currency = rules.find_total(text)
    return {
        "supplier_name": find_supplier(text),
        "invoice_number": rules.find_invoice_number(text),
        "invoice_date": rules.find_invoice_date(text),
        "total_amount": amount,
        "currency": currency,
        "line_items": rules.find_line_items(text),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--doc", required=True)
    args = p.parse_args()
    text = Path(args.doc).read_text(encoding="utf-8")
    print(json.dumps(extract(text), indent=2, default=str))


if __name__ == "__main__":
    main()
