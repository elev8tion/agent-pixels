def interactive(endpoint: str, model: str, verbose: bool):
    """Run interactive conversation loop."""
    print("PixelRAG Agent (Claude + visual search)")
    print(f"  endpoint: {endpoint}")
    print(f"  model:    {model}")
    print("  Type 'quit' to exit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question or question.lower() in ("quit", "exit", "q"):
            break

        print()
        try:
            answer = run_agent(question, endpoint, model, verbose)
            print(f"Agent: {answer}\n")
        except anthropic.APIError as e:
            print(f"API error: {e}\n")
        except Exception as e:
            print(f"Error: {e}\n")
