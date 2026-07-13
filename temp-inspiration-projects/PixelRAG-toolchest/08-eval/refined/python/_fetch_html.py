def _fetch_html(self, article_id: int) -> str | None:
        """Fetch article HTML from kiwix-serve (with caching)."""
        if article_id in self._html_cache:
            return self._html_cache[article_id]

        if article_id >= len(self._articles):
            return None

        import requests
        from urllib.parse import quote

        slug = self._articles[article_id]
        url = f"{self.KIWIX_BASE}/{quote(slug, safe='/:@!$&()*+,;=')}"
        try:
            resp = requests.get(url, timeout=15)
            resp.encoding = "utf-8"
            if resp.status_code != 200:
                return None
            self._html_cache[article_id] = resp.text
            return resp.text
        except Exception:
            return None
