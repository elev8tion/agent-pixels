def parse_model_output(text: str) -> dict | None:
    if not text or text.strip() == "SKIP":
        return None
    fields = {}
    for line in text.splitlines():
        line = line.strip()
        for prefix, key in [
            ("Q:", "query"),
            ("A:", "answer"),
            ("S:", "source_sentence"),
            ("T:", "source_type"),
        ]:
            if line.startswith(prefix):
                fields[key] = line[len(prefix) :].strip()
                break
    if (
        not fields.get("query")
        or not fields.get("answer")
        or not fields.get("source_sentence")
    ):
        return None
    return {
        "query": fields["query"],
        "answer": fields["answer"],
        "source_sentence": fields["source_sentence"],
        "source_type": fields.get("source_type", "prose"),
    }
