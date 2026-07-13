def _ondemand_chunk_b64(
    article_id: int, tile_index: int, chunk_index: int, tile_height: int
):
    """Render+chunk the page on demand and return the chunk as base64 PNG."""
    od = _state.get("ondemand")
    if od is None:
        return None
    p = od.chunk_path(article_id, _resolve_url(article_id), tile_index, chunk_index)
    if not p or not os.path.exists(p):
        return None
    import io

    from PIL import Image

    im = Image.open(p)
    # The on-demand render captures a full tile_height; trim the (padded) last
    # chunk back to the height the index recorded so it matches the built tile.
    if tile_height and im.height > tile_height:
        im = im.crop((0, 0, im.width, tile_height))
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()
