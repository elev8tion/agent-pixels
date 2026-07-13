def main() -> None:
    """CLI entry point: pixelshot.

    Usage examples::

        # Single URL, default CDP backend
        pixelshot https://example.com --output ./tiles

        # Multiple inputs with 4 workers
        pixelshot https://a.com https://b.com --output ./tiles --workers 4

        # PDF
        pixelshot report.pdf --output ./tiles

        # Local HTML
        pixelshot index.html --output ./tiles --backend playwright

        # Pipe URLs from a file
        cat urls.txt | xargs pixelshot --output ./tiles --workers 8

        # Chrome management (folded from the former `pixelrag-chrome`)
        pixelshot install-chrome   # download the patched headless Chrome
        pixelshot which-chrome     # print the active Chrome binary path
    """
    # Chrome management subcommands — dispatch before building the render parser.
    if len(sys.argv) > 1 and sys.argv[1] in ("install-chrome", "which-chrome"):
        from pixelrag_render import chrome

        if sys.argv[1] == "install-chrome":
            chrome.install_chrome()
        else:
            try:
                print(chrome.find_chrome(auto_install=False))
            except FileNotFoundError as e:
                print(str(e), file=sys.stderr)
                sys.exit(1)
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="pixelshot",
        description="Render documents (URLs, PDFs, HTML files) to tiled JPEG images.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="INPUT",
        help="URLs or file paths to render.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="./tiles",
        metavar="DIR",
        help="Output directory for tile subdirectories (default: ./tiles).",
    )
    parser.add_argument(
        "--backend",
        choices=["cdp", "playwright"],
        default="cdp",
        help="Browser backend for URL/HTML rendering (default: cdp).",
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of parallel browser processes (default: 4).",
    )
    parser.add_argument(
        "--tile-height",
        type=int,
        default=8192,
        help="Maximum tile height in pixels (default: 8192).",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG quality 1-100 (default: 85).",
    )
    parser.add_argument(
        "--viewport-width",
        type=int,
        default=875,
        help="Browser viewport width in pixels (default: 875).",
    )
    parser.add_argument(
        "--wait-network-idle",
        action="store_true",
        help="After the page's load event, also wait until the network is quiet "
        "(~500ms) before capturing. Helps JS/SPA pages that fetch content after "
        "load; adds a quiet window per page, so off by default. Recommended for "
        "single-page renders (e.g. the pixelbrowse skill).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="DPI for PDF rendering (default: 200).",
    )
    parser.add_argument(
        "--cdp-url",
        default=os.environ.get("PIXELSHOT_CDP_URL"),
        metavar="URL",
        help="Attach to an already-running Chrome/Brave DevTools endpoint "
        "(e.g. http://127.0.0.1:9222) instead of launching a throwaway headless "
        "browser. Renders each input in a fresh tab using that browser's existing "
        "session (cookies/logins) — so authenticated pages work — then closes only "
        "that tab. Needs no local Chrome binary. Env: PIXELSHOT_CDP_URL.",
    )

    args = parser.parse_args()
    output_dir = Path(args.output)

    # Partition inputs into URLs and files for batch processing
    urls = []
    files = []
    for inp in args.inputs:
        if inp.startswith("http://") or inp.startswith("https://"):
            urls.append(inp)
        else:
            files.append(Path(inp))

    results: list[Path] = []

    # Batch-render URLs together for efficiency
    if urls:
        logger.info(
            "Rendering %d URL(s) with backend=%s workers=%d",
            len(urls),
            args.backend,
            args.workers,
        )
        tile_dirs = render_urls(
            urls,
            output_dir,
            backend=args.backend,
            tile_height=args.tile_height,
            quality=args.quality,
            viewport_width=args.viewport_width,
            workers=args.workers,
            wait_network_idle=args.wait_network_idle,
            cdp_url=args.cdp_url,
        )
        results.extend(tile_dirs)

    # Handle files individually (they may need different backends)
    for fpath in files:
        suffix = fpath.suffix.lower()
        try:
            if suffix == ".pdf":
                tile_dirs = render_pdf(
                    fpath, output_dir, dpi=args.dpi, quality=args.quality
                )
            elif suffix in {".html", ".htm"}:
                file_url = fpath.resolve().as_uri()
                tile_dirs = render_url(
                    file_url,
                    output_dir,
                    backend=args.backend,
                    tile_height=args.tile_height,
                    quality=args.quality,
                    viewport_width=args.viewport_width,
                    workers=1,
                    wait_network_idle=args.wait_network_idle,
                    cdp_url=args.cdp_url,
                )
            elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
                tile_dirs = render_file(fpath, output_dir)
            else:
                logger.warning("Unsupported file type: %s — skipping", fpath)
                continue
            results.extend(tile_dirs)
        except Exception as e:
            logger.error("Failed to render %s: %s", fpath, e)

    if results:
        logger.info("Done. %d output(s):", len(results))
        for r in results:
            print(r)
    else:
        logger.warning("No outputs produced.")
        sys.exit(1)
