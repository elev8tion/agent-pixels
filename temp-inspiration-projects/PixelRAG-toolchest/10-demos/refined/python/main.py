def main() -> None:
    from pixelrag_render.render import render_file

    # Clean previous output
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    print("=" * 60)
    print("  PixelRAG Ingest Demo: Heterogeneous Documents")
    print("=" * 60)
    print()

    # --- Step 1: Create sample local HTML ---
    print("[1] Creating sample HTML files...")
    html_files = create_sample_html(OUTPUT)
    for f in html_files:
        print(f"    {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    print()

    tiles_dir = OUTPUT / "tiles"
    tiles_dir.mkdir()
    all_results: list[tuple[str, int, float]] = []

    # --- Step 2: Render Wikipedia URLs ---
    print(f"[2] Rendering {len(WIKI_URLS)} Wikipedia articles (CDP backend)...")
    t0 = time.time()
    from pixelrag_render.render import render_urls

    url_tiles = render_urls(WIKI_URLS, str(tiles_dir), backend="cdp", workers=3)
    elapsed = time.time() - t0
    for td in url_tiles:
        n = len(list(td.glob("tile_*")))
        name = td.name.replace(".png.tiles", "")
        all_results.append((f"URL: {name}", n, elapsed / len(WIKI_URLS)))
    print(f"    {len(url_tiles)} pages rendered in {elapsed:.1f}s")
    print()

    # --- Step 3: Render local HTML files ---
    print(f"[3] Rendering {len(html_files)} local HTML files...")
    for html_file in html_files:
        t0 = time.time()
        result = render_file(str(html_file), str(tiles_dir), backend="cdp")
        elapsed = time.time() - t0
        for td in result:
            n = len(list(Path(td).glob("tile_*")))
            all_results.append((f"HTML: {html_file.name}", n, elapsed))
    print(f"    {len(html_files)} files rendered")
    print()

    # --- Summary ---
    print("=" * 60)
    print("  Results")
    print("=" * 60)
    total_tiles = 0
    for name, n_tiles, elapsed in all_results:
        total_tiles += n_tiles
        print(f"  {name:<45} {n_tiles:>3} tiles  {elapsed:.1f}s")
    print(f"  {'─' * 55}")
    print(f"  {'TOTAL':<45} {total_tiles:>3} tiles")
    print()

    # Show output structure
    print("Output structure:")
    for td in sorted(tiles_dir.iterdir()):
        if td.is_dir():
            tiles = list(td.glob("tile_*"))
            size = sum(t.stat().st_size for t in tiles) / 1024
            print(f"  {td.name}/")
            print(f"    {len(tiles)} tiles, {size:.0f} KB total")
    print()
    print(f"All output in: {tiles_dir}")
