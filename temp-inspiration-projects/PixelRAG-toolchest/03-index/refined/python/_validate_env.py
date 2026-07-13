def _validate_env() -> dict[str, str]:
    """Build env dict with GOOGLE_API_KEY for validate_tiles.py subprocess."""
    env = os.environ.copy()
    env.pop("GEMINI_API_KEY", None)  # avoid "both keys set" warning
    return env
