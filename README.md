# NLP → LLM Extraction Pipeline (Phased Evolution)

Demonstrates the **three-phase evolution** of a structured-extraction pipeline for supplier documents — from rule-based NER through to LLM-with-schema-enforcement. Each phase is runnable; the eval harness compares them head-to-head on the same dataset.

> Mirrors the production NLP→LLM pipeline I built at Limendo (2022–2025) that eliminated ~200 weekly manual data-entry tasks.

---

## Why This Repo Exists

Most "I used GPT-4 for extraction" demos skip the boring story: the *real* journey was three phases over 18 months. This repo preserves that journey so you can compare:

| Phase | Stack | When | Strengths | Weaknesses |
|---|---|---|---|---|
| **Phase 1** | SpaCy NER + regex rules | 2022 | Fast, deterministic, no API cost | Brittle on layout drift; hard to extend |
| **Phase 2** | GPT-3.5 + raw prompt | early 2023 | Handles unseen layouts | JSON output unreliable; ~10% parse failures |
| **Phase 3** | GPT-4 + LangChain + Pydantic schema | mid 2023 | Schema-enforced output, retry on validation fail | More expensive per call |

---

## Quickstart

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
export OPENAI_API_KEY=sk-...        # only needed for phase 2 + 3

# Run a single document through each phase
python -m phase1_spacy.extract --doc data/samples/invoice_001.txt
python -m phase2_gpt35.extract  --doc data/samples/invoice_001.txt
python -m phase3_langchain.extract --doc data/samples/invoice_001.txt

# Compare all three on the eval set
python -m eval.compare --eval-set data/eval/eval_set.json
```

---

## Output Schema (Phase 3 enforces this)

```python
class SupplierInvoice(BaseModel):
    supplier_name: str
    invoice_number: str
    invoice_date: date
    total_amount: float
    currency: str
    line_items: list[LineItem]
```

Phase 1 returns a flat dict. Phase 2 returns whatever GPT-3.5 felt like. Phase 3 returns a validated `SupplierInvoice` or raises (after one retry).

---

## Repository Layout

```
nlp-to-llm-extraction-pipeline/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── .env.example
├── data/
│   ├── samples/
│   │   ├── invoice_001.txt
│   │   ├── invoice_002.txt
│   │   └── invoice_003.txt
│   └── eval/
│       └── eval_set.json
├── schema/
│   ├── __init__.py
│   └── models.py                  # Pydantic models shared across phases
├── phase1_spacy/
│   ├── __init__.py
│   ├── ner_patterns.py            # custom SpaCy patterns
│   ├── rules.py                   # regex extractors
│   └── extract.py                 # phase 1 entrypoint
├── phase2_gpt35/
│   ├── __init__.py
│   └── extract.py                 # raw OpenAI prompt
├── phase3_langchain/
│   ├── __init__.py
│   ├── prompts.py
│   └── extract.py                 # LangChain + Pydantic schema enforcement
└── eval/
    ├── __init__.py
    ├── metrics.py
    └── compare.py                 # head-to-head eval harness
```

---

## Eval Harness Output (sample)

| Phase | Field accuracy | JSON parse rate | Cost / 1k docs |
|---|---|---|---|
| Phase 1 (SpaCy + rules) | 0.74 | 1.00 | $0 |
| Phase 2 (GPT-3.5 raw) | 0.86 | 0.91 | ~$0.50 |
| Phase 3 (GPT-4 + schema) | 0.94 | 1.00 | ~$10 |

> Numbers are illustrative. Real production gain was the **JSON parse rate** going from 0.91 → 1.00 — that's what eliminated the manual-fix queue.

---

## Production Notes

- The actual pipeline ran on **AWS Lambda** behind **API Gateway**, with extracted records landing in **S3 → Athena**.
- Schema validation failures emitted a **CloudWatch metric** that fed the retraining + prompt-iteration loop.
- Phase 3's LangChain `OutputParser` retry path was critical — it converts a soft "validation failed" into a hard "model gets one more chance with the validation error appended" without manual intervention.

---

## License

MIT
