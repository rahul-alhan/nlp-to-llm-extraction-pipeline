SYSTEM = """You are a precise extraction engine. Output only data that is
literally present in the invoice text. Do not invent suppliers, dates,
or amounts. If a field is missing, leave it null. Output must conform
to the provided JSON schema exactly."""

USER = """Invoice text:
{text}

Extract supplier_name, invoice_number, invoice_date, total_amount,
currency, and line_items per the schema."""

RETRY = """Your previous output failed validation:
{error}

Re-emit valid JSON conforming to the schema. Do not change extracted
values; only fix structural / type issues."""
