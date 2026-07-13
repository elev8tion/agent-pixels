def _usage() -> str:
    rows = "\n".join(f"  {name:<13} {mod[0]}" for name, mod in STAGES.items())
    return (
        "usage: pixelrag <stage> [args...]\n\n"
        "Pipeline stages:\n"
        f"{rows}\n\n"
        "Capture a page to screenshot tiles with the standalone `pixelshot` command.\n"
        "Run `pixelrag <stage> --help` for a stage's own options."
    )
