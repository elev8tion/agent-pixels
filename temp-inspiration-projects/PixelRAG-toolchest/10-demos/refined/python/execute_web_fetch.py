def execute_web_fetch(url: str) -> dict:
    """Fetch text from a URL (simplified — returns first 4000 chars)."""
    req = urllib.request.Request(url, headers={"User-Agent": "PixelRAG-Agent/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8", errors="replace")

    # Strip HTML tags for a rough text extraction
    import re

    text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return {"url": url, "content": text[:4000], "truncated": len(text) > 4000}
