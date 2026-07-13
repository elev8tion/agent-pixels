def _read_entry(self, entry_path: str) -> tuple[bytes, str] | None:
        """Read from ZIM (runs in thread pool)."""
        if not self.archive.has_entry_by_path(entry_path):
            return None
        entry = self.archive.get_entry_by_path(entry_path)
        item = entry.get_item()
        content = bytes(item.content)
        mimetype = item.mimetype.split(";")[0].strip()
        return content, mimetype
