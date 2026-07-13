def _parse_ssh_spec(spec: str) -> tuple[str, str]:
    """Parse ``user@host:/project/dir`` → ``('user@host', '/project/dir')``.

    If no ``:path`` part, defaults to ``~/pixelrag-index``.
    """
    colon_idx = spec.find(":/")
    if colon_idx >= 0:
        return spec[:colon_idx], spec[colon_idx + 1 :]
    return spec, "~/pixelrag-index"
