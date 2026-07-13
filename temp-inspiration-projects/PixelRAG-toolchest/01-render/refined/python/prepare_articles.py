def prepare_articles(
    zim_path: str, n: int, seed: int = 42, kiwix_url: str | None = None
) -> list[dict]:
    """Sample articles from ZIM.

    kiwix_url can be:
    - None: write HTML to temp files (file:// mode)
    - "http://host:port": single kiwix-serve instance
    - "http://host:9461,http://host:9462,...": multiple instances (round-robin)
    """
    from libzim.reader import Archive
    from urllib.parse import quote

    archive = Archive(zim_path)

    # Support multiple kiwix URLs (comma-separated)
    kiwix_urls = kiwix_url.split(",") if kiwix_url else []
    # Detect book_name from first URL or ZIM filename
    if kiwix_urls:
        # Extract book_name from URL: http://host:port/content/{book_name}/...
        # For symlinks like wiki_1.zim, book_name = wiki_1
        # We need to figure out the right book_name for each URL
        pass
    book_name = Path(zim_path).stem
    rng = random.Random(seed)
    articles = []
    tried = 0
    while len(articles) < n and tried < n * 20:
        idx = rng.randint(0, archive.all_entry_count - 1)
        tried += 1
        try:
            e = archive._get_entry_by_id(idx)
            if e.is_redirect or e.path.startswith("-/") or len(e.path) <= 2:
                continue
            entry = archive.get_entry_by_path(e.path)
            item = entry.get_item()
            if "html" not in item.mimetype:
                continue
            html = bytes(item.content).decode("utf-8")
            if 'http-equiv="refresh"' in html.lower() or len(html) < 300:
                continue

            if kiwix_urls:
                safe = "/:@!$&'()*+,;="
                # Round-robin across kiwix instances
                base = kiwix_urls[len(articles) % len(kiwix_urls)]
                # Detect book_name from the symlink/ZIM each instance serves
                parts = base.rstrip("/").rsplit(":", 1)
                port = int(parts[1]) if len(parts) > 1 else 9454
                # Each instance may have different book_name (wiki_1, wiki_2, etc.)
                bname = f"wiki_{port - 9460}" if port > 9460 else book_name
                url = f"{base}/content/{bname}/{quote(e.path, safe=safe)}"
                articles.append({"path": e.path, "file": url})
            else:
                tmp = tempfile.NamedTemporaryFile(
                    suffix=".html", delete=False, dir="/tmp", prefix="bench_"
                )
                tmp.write(html.encode())
                tmp.close()
                articles.append({"path": e.path, "file": tmp.name})
        except Exception:
            continue
    return articles
