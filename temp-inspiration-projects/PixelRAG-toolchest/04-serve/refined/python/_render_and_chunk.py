def _render_and_chunk(self, article_id: int, title: str) -> None:
        from pixelrag_render import render_url
        from pixelrag_embed.chunk import chunk_article

        url = f"{self.kiwix_url}/content/{self.book}/{quote(title, safe='')}"
        staging = os.path.join(self.cache_dir, f".render_{article_id}")
        shutil.rmtree(staging, ignore_errors=True)
        dirs = render_url(
            url,
            staging,
            viewport_width=self.viewport_width,
            tile_height=self.tile_height,
        )
        if not dirs:
            shutil.rmtree(staging, ignore_errors=True)
            return
        rendered = str(dirs[0])  # <sanitized-url>.png.tiles/ (has tiles.json)
        chunk_article(rendered)  # writes chunk_XXXX_YY.png + chunks.json
        dest = self._article_dir(article_id)
        shutil.rmtree(dest, ignore_errors=True)
        os.replace(rendered, dest)  # atomic; commit only after chunking succeeds
        shutil.rmtree(staging, ignore_errors=True)
