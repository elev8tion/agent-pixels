def _render(self, hit: dict) -> str:
        from .text_renderer import render_text_chunk

        article_id = hit.get("article_id", "unknown")
        chunk_index = hit.get("chunk_index", 0)
        out_path = os.path.join(self.render_dir, f"{article_id}_{chunk_index}.png")
        if os.path.isfile(out_path):
            return out_path
        # No-title policy: mirrors `_hits_to_result` (line ~3035) — title/url are
        # leaked metadata for entity-answering tasks and were stripped from the
        # text→text path on 2026-04-29. Apply the same constraint here so
        # rendered and text→text differ only in modality, not in content.
        render_text_chunk(
            text=hit.get("text", ""),
            title=None,
            url=None,
            output_path=out_path,
        )
        return out_path
