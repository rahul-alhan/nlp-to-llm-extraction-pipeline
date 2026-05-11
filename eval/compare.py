"""Head-to-head eval harness across all three phases."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .metrics import field_accuracy

PHASES = ["phase1_spacy", "phase2_gpt35", "phase3_langchain"]


def _run_phase(phase: str, text: str) -> dict:
    if phase == "phase1_spacy":
        from phase1_spacy.extract import extract
        return extract(text)
    if phase == "phase2_gpt35":
        if not os.getenv("OPENAI_API_KEY"):
            return {"_parse_error": True, "_skipped": "no OPENAI_API_KEY"}
        from phase2_gpt35.extract import extract
        return extract(text)
    if phase == "phase3_langchain":
        if not os.getenv("OPENAI_API_KEY"):
            return {"_parse_error": True, "_skipped": "no OPENAI_API_KEY"}
        from phase3_langchain.extract import extract
        return extract(text).model_dump(mode="json")
    raise ValueError(phase)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eval-set", required=True)
    args = p.parse_args()

    cases = json.loads(Path(args.eval_set).read_text())
    summary = {ph: {"correct": 0, "total": 0, "parsed": 0, "n": 0} for ph in PHASES}

    for case in cases:
        text = Path(case["doc"]).read_text(encoding="utf-8")
        truth = case["ground_truth"]
        for ph in PHASES:
            pred = _run_phase(ph, text)
            res = field_accuracy(pred, truth)
            s = summary[ph]
            s["correct"] += res["correct"]
            s["total"] += res["total"]
            s["parsed"] += int(res["parsed"])
            s["n"] += 1

    print("\n=== Phase comparison ===")
    print(f"{'Phase':<20} {'Acc':>8} {'ParseRate':>11}")
    for ph, s in summary.items():
        acc = s["correct"] / max(1, s["total"])
        parse_rate = s["parsed"] / max(1, s["n"])
        print(f"{ph:<20} {acc:>8.3f} {parse_rate:>11.3f}")


if __name__ == "__main__":
    main()
