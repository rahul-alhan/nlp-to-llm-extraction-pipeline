"""Phase 2 — raw GPT-3.5 prompt; JSON parse rate ~0.91 in production."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from openai import OpenAI

PROMPT = """Extract structured fields from the supplier invoice.
Return JSON with keys:
  supplier_name, invoice_number, invoice_date (YYYY-MM-DD),
  total_amount (number), currency (3-letter), line_items (list of
  {{description, quantity, unit_price, line_total}}).

Invoice:
{text}

JSON:"""


def extract(text: str, model: str = "gpt-3.5-turbo") -> dict:
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT.format(text=text)}],
        temperature=0,
    )
    raw = resp.choices[0].message.content
    # Phase 2 reality: GPT-3.5 sometimes wraps JSON in prose / markdown fences
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    blob = m.group(0) if m else raw
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return {"_parse_error": True, "raw": raw}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--doc", required=True)
    args = p.parse_args()
    text = Path(args.doc).read_text(encoding="utf-8")
    print(json.dumps(extract(text), indent=2, default=str))


if __name__ == "__main__":
    main()
