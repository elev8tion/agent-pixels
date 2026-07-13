def parse_json_from_text(text: str):
    text = text.strip()
    if not text:
        raise ValueError("empty response")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", text)
    if not match:
        raise ValueError("no JSON object or array found")
    return json.loads(match.group(1))
