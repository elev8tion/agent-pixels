def build_client(args: argparse.Namespace) -> dict:
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", args.gemini_project)
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", args.gemini_location)

    from google import genai
    from google.genai.types import HttpOptions

    client = genai.Client(http_options=HttpOptions(api_version="v1"))
    return {
        "client": client,
        "usage": init_usage(),
        "usage_lock": threading.Lock(),
    }
