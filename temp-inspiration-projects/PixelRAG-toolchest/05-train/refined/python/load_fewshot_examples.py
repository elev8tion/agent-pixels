def load_fewshot_examples(path: Path | None) -> list[dict]:
    if path is not None:
        with open(path) as f:
            return [json.loads(line) for line in f if line.strip()]
    return BUILTIN_FEWSHOT
