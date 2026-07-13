def _fetch_json(url: str, cdp_url: str, timeout: float = 5):
    """GET ``url`` and parse JSON, mapping connection failures to a clear error.

    ``cdp_url`` is the user-facing endpoint, used only for the message so a bad
    or unreachable ``--cdp-url`` surfaces an actionable error instead of a raw
    URLError traceback.
    """
    try:
        data = urllib.request.urlopen(url, timeout=timeout).read()
        return json.loads(data)
    except Exception as e:
        raise RuntimeError(f"Could not reach CDP endpoint at {cdp_url}: {e}") from e
