def handle_tool_call(tool_name: str, tool_input: dict, endpoint: str) -> str:
    """Execute a tool call and return the result as a string."""
    try:
        if tool_name == "pixelrag_search":
            result = execute_pixelrag_search(
                query=tool_input["query"],
                n_results=tool_input.get("n_results", 5),
                endpoint=endpoint,
            )
        elif tool_name == "web_fetch":
            result = execute_web_fetch(url=tool_input["url"])
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        result = {"error": str(e)}
    return json.dumps(result)
