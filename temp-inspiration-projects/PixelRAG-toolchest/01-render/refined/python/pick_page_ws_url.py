def pick_page_ws_url(targets: list[dict]) -> str:
    """Return the webSocketDebuggerUrl for a ``type: page`` target.

    Chrome's ``/json`` endpoint may list ``background_page`` targets (from
    built-in extensions like Cast / Media Router) before real page targets.
    Connecting to a ``background_page`` hangs because it ignores
    ``Page.navigate``.  Filter for ``type == "page"`` first; fall back to
    the unfiltered list so pre-existing behaviour is preserved when Chrome
    reports no page targets at all.
    """
    pages = [t for t in targets if t.get("type") == "page"] or targets
    return pages[0]["webSocketDebuggerUrl"]
