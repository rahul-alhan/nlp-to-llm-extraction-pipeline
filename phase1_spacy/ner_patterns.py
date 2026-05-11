"""Custom SpaCy patterns for supplier-name detection."""
from __future__ import annotations

SUPPLIER_PATTERNS = [
    [{"LOWER": "supplier"}, {"IS_PUNCT": True, "OP": "?"}, {"IS_TITLE": True, "OP": "+"}],
    [{"LOWER": "from"}, {"IS_TITLE": True, "OP": "+"}, {"LOWER": {"IN": ["ltd", "llp", "inc", "corp", "gmbh", "pvt"]}}],
    [{"IS_TITLE": True, "OP": "+"}, {"LOWER": {"IN": ["ltd", "llp", "inc", "corp", "gmbh", "pvt"]}}],
]
