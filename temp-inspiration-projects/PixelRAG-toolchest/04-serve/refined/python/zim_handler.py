class ZimHandler(BaseHTTPRequestHandler):
    archive = None
    book_name = None

    def do_HEAD(self):
        self._handle(head_only=True)

    def do_GET(self):
        self._handle(head_only=False)

    def _handle(self, head_only=False):
        path = unquote(self.path)

        # Strip /content/{book_name}/ prefix
        prefix = f"/content/{self.book_name}/"
        if path.startswith(prefix):
            entry_path = path[len(prefix) :]
        elif path.startswith("/"):
            entry_path = path[1:]
        else:
            entry_path = path

        # Strip query string
        if "?" in entry_path:
            entry_path = entry_path.split("?")[0]

        try:
            if not self.archive.has_entry_by_path(entry_path):
                self.send_error(404, f"Not found: {entry_path}")
                return

            entry = self.archive.get_entry_by_path(entry_path)
            item = entry.get_item()
            content = bytes(item.content)
            mimetype = item.mimetype.split(";")[0].strip()

            self.send_response(200)
            self.send_header("Content-Type", mimetype)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            if not head_only:
                self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        pass  # suppress access logs
