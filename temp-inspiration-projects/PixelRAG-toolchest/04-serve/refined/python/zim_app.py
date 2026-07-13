class ZimApp:
    def __init__(self, zim_path: str, workers: int = 32):
        self.archive = Archive(zim_path)
        self.book_name = Path(zim_path).stem
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self.loop = None

    def _read_entry(self, entry_path: str) -> tuple[bytes, str] | None:
        """Read from ZIM (runs in thread pool)."""
        if not self.archive.has_entry_by_path(entry_path):
            return None
        entry = self.archive.get_entry_by_path(entry_path)
        item = entry.get_item()
        content = bytes(item.content)
        mimetype = item.mimetype.split(";")[0].strip()
        return content, mimetype

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
