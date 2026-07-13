def _derive_kiwix_book(kiwix_url: str) -> str:
    """Read the kiwix-serve catalog and return the /content/<book> id."""
    import re
    import urllib.request

    try:
        with urllib.request.urlopen(
            kiwix_url.rstrip("/") + "/catalog/v2/entries", timeout=10
        ) as r:
            xml = r.read().decode()
        m = re.search(r'href="/content/([^"/]+)"', xml)
        return m.group(1) if m else ""
    except Exception:
        return ""
