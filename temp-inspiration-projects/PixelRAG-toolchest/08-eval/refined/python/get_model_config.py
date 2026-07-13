def get_model_config(model_name: str) -> Dict[str, Optional[str]]:
    """
    Get model configuration based on model name.

    Args:
        model_name: Name of the model (e.g., 'Qwen/Qwen3-VL-4B-Instruct', 'gemini-3-pro-preview')

    Returns:
        Dictionary with 'api_base', 'api_key', and 'model' keys.
    """
    model_lower = model_name.lower()

    # Gemini models
    if "gemini" in model_lower:
        # Check for Vertex AI first
        vertex_api_key = os.getenv("GEMINI_API_KEY")
        use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"

        if use_vertex and vertex_api_key:
            # Using Vertex AI - don't pass api_key, use environment variable instead
            api_key = None  # Vertex AI uses environment variable, not api_key parameter
        else:
            # Using standard Gemini API
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required for Gemini models. "
                    "Set it with: export GOOGLE_API_KEY='your-api-key' or export GEMINI_API_KEY='your-api-key' and GOOGLE_GENAI_USE_VERTEXAI=true"
                )

        # For Gemini models, we use Google's Generative AI SDK directly
        # The api_base is not used for Gemini (SDK handles it internally)
        # But we set a placeholder for compatibility
        api_base = None  # Not used for Gemini SDK

        return {
            "api_base": api_base,
            "api_key": api_key,
            "model": model_name,  # Use the model name as-is
        }

    # Default: assume OpenAI-compatible API (vLLM, etc.)
    return {
        "api_base": os.getenv("API_BASE", "http://localhost:8000/v1"),
        "api_key": os.getenv("API_KEY", "dummy"),
        "model": model_name,
    }
