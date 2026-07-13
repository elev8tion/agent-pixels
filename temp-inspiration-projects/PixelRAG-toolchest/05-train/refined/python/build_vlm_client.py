def build_vlm_client(args: argparse.Namespace) -> dict:
    provider = "gemini" if args.gemini else args.provider
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        return {
            "provider": "openai",
            "api_key": api_key,
            "usage": init_token_usage(),
            "usage_lock": threading.Lock(),
        }

    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", args.gemini_project)
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", args.gemini_location)
    from google import genai
    from google.genai.types import HttpOptions

    client = genai.Client(http_options=HttpOptions(api_version="v1"))
    return {
        "provider": "gemini",
        "client": client,
        "usage": init_token_usage(),
        "usage_lock": threading.Lock(),
    }
