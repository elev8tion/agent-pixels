def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(_usage())
        sys.exit(0 if len(sys.argv) >= 2 else 2)

    stage = sys.argv[1]
    if stage not in STAGES:
        print(f"pixelrag: unknown stage '{stage}'\n\n{_usage()}", file=sys.stderr)
        sys.exit(2)

    module, func, package, extra = STAGES[stage]
    try:
        mod = importlib.import_module(module)
    except ModuleNotFoundError:
        print(
            f"pixelrag: stage '{stage}' is not installed.\n"
            f"  → uv sync --package {package}   (dev)\n"
            f"  → pip install 'pixelrag[{extra}]'   (published)",
            file=sys.stderr,
        )
        sys.exit(1)

    # Hand argv to the stage's own argparse; prog reads as `pixelrag <stage>`.
    sys.argv = [f"pixelrag {stage}", *sys.argv[2:]]
    getattr(mod, func)()
