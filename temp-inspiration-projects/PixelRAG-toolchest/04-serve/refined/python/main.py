def main():
    parser = argparse.ArgumentParser(description="Async ZIM HTTP server")
    parser.add_argument("--zim", required=True)
    parser.add_argument("--port", type=int, default=9454)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()

    app_state = ZimApp(args.zim, workers=args.workers)

    app = web.Application()
    app.router.add_route("*", "/{path:.*}", app_state.handle)

    async def on_startup(app):
        app_state.loop = asyncio.get_event_loop()

    app.on_startup.append(on_startup)

    print(
        f"Async ZIM server: http://{args.host}:{args.port}/content/{app_state.book_name}/"
    )
    print(f"ZIM: {args.zim} ({app_state.archive.article_count:,} articles)")
    print(f"Thread pool: {args.workers} workers")

    web.run_app(app, host=args.host, port=args.port, print=None)
