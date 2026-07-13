def _is_article_path(self, path: str) -> bool:
        if not path:
            return False
        if any(path.startswith(p) for p in self._SKIP_PREFIXES):
            return False
        if path in self._SKIP_EXACT:
            return False
        if "." in path.rsplit("/", 1)[-1]:
            last_part = path.rsplit("/", 1)[-1]
            ext = last_part.rsplit(".", 1)[-1].lower()
            if ext in {
                "png",
                "jpg",
                "jpeg",
                "gif",
                "svg",
                "webp",
                "ico",
                "css",
                "js",
                "json",
                "woff",
                "woff2",
                "ttf",
                "eot",
                "tif",
                "tiff",
                "bmp",
                "mp3",
                "mp4",
                "ogg",
                "ogv",
                "webm",
                "flac",
                "wav",
                "opus",
                "mid",
            }:
                return False
        return True
