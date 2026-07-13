def _derive_stems(urls: list[str], stems: list[str] | None) -> list[str]:
    """Output-dir stem per URL (explicit stems win; else sanitize the URL).

    Shared by the standard and turbo paths so both emit identical
    ``{stem}.png.tiles`` directory names for the same inputs.
    """
    from urllib.parse import urlparse

    out: list[str] = []
    seen: dict[str, int] = {}
    for i, url in enumerate(urls):
        if stems and i < len(stems):
            out.append(str(stems[i]))
            continue
        parsed = urlparse(url)
        raw = (parsed.netloc + parsed.path).rstrip("/")
        stem = (
            raw.replace("/", "_").replace(":", "_").replace("?", "_").replace("&", "_")
        )
        stem = stem[:200] or "page"
        count = seen.get(stem, 0)
        seen[stem] = count + 1
        if count > 0:
            stem = f"{stem}_{count}"
        out.append(stem)
    return out
