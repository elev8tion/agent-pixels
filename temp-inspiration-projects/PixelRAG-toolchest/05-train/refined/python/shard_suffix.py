def shard_suffix(p: str) -> str:
    parts = p.split("/")
    for i, x in enumerate(parts):
        if x.startswith("shard_"):
            return "/".join(parts[i:])
    return p
