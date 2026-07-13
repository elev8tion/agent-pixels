def _generate_html_report(results: list[dict], html_path: Path) -> None:
    """Generate an HTML page showing search results with tile images."""
    import base64

    rows = []
    for r in results:
        query = r["query"]
        rows.append(f'<h2>Q: "{query}"</h2>')
        for i, h in enumerate(r.get("hits", [])[:3]):
            url = h.get("url", "")
            title = (
                url.split("/")[-1].replace("_", " ") if url else f"#{h['article_id']}"
            )
            score = h["score"]
            tile_html = ""
            tile_path = h.get("_tile_path")
            if tile_path and Path(tile_path).exists():
                data = Path(tile_path).read_bytes()
                ext = Path(tile_path).suffix.lstrip(".")
                b64 = base64.b64encode(data).decode()
                tile_html = f'<img src="data:image/{ext};base64,{b64}" style="max-width:600px;border:1px solid #ddd;border-radius:4px;">'
            rows.append(f"""
            <div style="margin:1em 0;padding:1em;border:1px solid #222;border-radius:8px;background:#111;">
              <div style="color:#4a9eff;font-weight:600;">{i + 1}. {score:.3f} — {title}</div>
              {f'<div style="margin-top:0.5em;">{tile_html}</div>' if tile_html else ""}
            </div>""")

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>PixelRAG E2E Results</title>
<style>body{{font-family:system-ui;background:#0a0a0a;color:#e0e0e0;max-width:800px;margin:2em auto;padding:0 1em;}}
h1{{color:#fff;}}h2{{color:#aaa;margin-top:2em;}}</style></head>
<body><h1>PixelRAG Search Results</h1>
{"".join(rows)}
</body></html>"""
    html_path.write_text(html)
