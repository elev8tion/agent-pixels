def build_openai_client(api_base_url="", timeout=60):
    """Create an OpenAI-compatible client for local or hosted endpoints."""
    from openai import OpenAI  # pyright: ignore[reportMissingImports]

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_base_url:
        # Local vLLM endpoints use their own auth; don't leak OPENAI_API_KEY
        vllm_key = os.environ.get("VLLM_API_KEY", "dummy")
        return OpenAI(base_url=api_base_url, api_key=vllm_key, timeout=timeout)
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Provide an OpenAI key or pass --vllm-url "
            "for a local OpenAI-compatible endpoint."
        )
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base, timeout=timeout)
