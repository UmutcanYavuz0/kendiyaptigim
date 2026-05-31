import json


def clean_and_parse(raw: str) -> dict:
    """Strip markdown fences and parse JSON string into a dict."""
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    raw = raw.rstrip("`").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}\n{raw}")
