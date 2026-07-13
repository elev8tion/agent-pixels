def gt_cache_key(articles: list[dict], seed: int) -> str:
    paths = sorted(a["path"] for a in articles)
    content = f"seed={seed}\n" + "\n".join(paths)
    return hashlib.sha256(content.encode()).hexdigest()[:16]
