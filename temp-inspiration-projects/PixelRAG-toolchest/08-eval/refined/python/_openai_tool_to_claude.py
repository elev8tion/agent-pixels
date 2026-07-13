def _openai_tool_to_claude(schema: dict) -> dict:
    fn = schema["function"]
    return {
        "name": fn["name"],
        "description": fn["description"],
        "input_schema": fn["parameters"],
    }
