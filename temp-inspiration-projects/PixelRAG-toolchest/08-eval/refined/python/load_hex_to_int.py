def load_hex_to_int(path: str) -> dict[str, int]:
    with open(path) as f:
        return json.load(f)
