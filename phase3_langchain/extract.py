"""Phase 3 — GPT-4 + LangChain + Pydantic schema enforcement with retry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from schema.models import SupplierInvoice
from . import prompts as P


def _llm():
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


def extract(text: str) -> SupplierInvoice:
    parser = PydanticOutputParser(pydantic_object=SupplierInvoice)
    tpl = ChatPromptTemplate.from_messages(
        [
            ("system", P.SYSTEM + "\n\n{format_instructions}"),
            ("user", P.USER),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    chain = tpl | _llm()
    raw = chain.invoke({"text": text}).content

    try:
        return parser.parse(raw)
    except ValidationError as exc:
        # one retry with the validation error appended
        retry_tpl = ChatPromptTemplate.from_messages(
            [("system", P.SYSTEM), ("user", P.USER), ("user", P.RETRY)]
        ).partial(format_instructions=parser.get_format_instructions())
        retry_raw = (retry_tpl | _llm()).invoke(
            {"text": text, "error": str(exc)}
        ).content
        return parser.parse(retry_raw)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--doc", required=True)
    args = p.parse_args()
    text = Path(args.doc).read_text(encoding="utf-8")
    invoice = extract(text)
    print(json.dumps(invoice.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    main()
