async def handle(self, request: web.Request) -> web.Response:
        path = unquote(request.path)

        prefix = f"/content/{self.book_name}/"
        if path.startswith(prefix):
            entry_path = path[len(prefix) :]
        elif path.startswith("/"):
            entry_path = path[1:]
        else:
            entry_path = path

        if "?" in entry_path:
            entry_path = entry_path.split("?")[0]

        result = await self.loop.run_in_executor(
            self.pool, self._read_entry, entry_path
        )

        if result is None:
            return web.Response(status=404, text=f"Not found: {entry_path}")

        content, mimetype = result
        return web.Response(
            body=content,
            content_type=mimetype,
            headers={"Cache-Control": "public, max-age=3600"},
        )
