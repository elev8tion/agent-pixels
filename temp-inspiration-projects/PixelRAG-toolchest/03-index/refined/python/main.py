def main():
    parser = argparse.ArgumentParser(description="Build a visual search index")
    parser.add_argument("command", choices=["build"])
    parser.add_argument("--config", "-c", default=None, help="Path to pixelrag.yaml")
    parser.add_argument(
        "--source", "-s", default=None, help="Source path (overrides config)"
    )
    parser.add_argument(
        "--source-type", default=None, help="Source type (kiwix/web/pdf/local)"
    )
    parser.add_argument("--output", "-o", default=None, help="Output directory")
    parser.add_argument(
        "--device", default=None, choices=["cpu", "cuda"], help="Embedding device"
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=None, help="Max documents to process"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Clean output and rebuild from scratch",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    config = load_config(args.config)

    if args.source:
        config.setdefault("source", {})["path"] = args.source
    if args.source_type:
        config.setdefault("source", {})["type"] = args.source_type
    if args.output:
        config["output"] = args.output
    if args.device:
        config.setdefault("embed", {})["device"] = args.device

    if args.command == "build":
        build(config, limit=args.limit, force=args.force)
