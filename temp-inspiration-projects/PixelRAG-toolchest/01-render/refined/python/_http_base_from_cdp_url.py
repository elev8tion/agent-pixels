def _http_base_from_cdp_url(cdp_url: str) -> str:
    """Normalize a ``--cdp-url`` value to an http DevTools base ``http://host:port``.

    Accepts ``http://host:port`` (any path is ignored), ``ws://host:port/...``
    (scheme swapped to http, path dropped), or a bare ``host:port``.
    """
    from urllib.parse import urlparse

    p = urlparse(cdp_url if "//" in cdp_url else f"//{cdp_url}")
    netloc = p.netloc or p.path
    if not netloc:
        raise ValueError(f"Invalid --cdp-url: {cdp_url!r}")
    return f"http://{netloc}"
