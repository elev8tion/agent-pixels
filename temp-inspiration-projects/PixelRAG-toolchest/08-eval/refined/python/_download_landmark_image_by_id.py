def _download_landmark_image_by_id(img_id: str, local_path: str) -> bool:
    """Download a landmark image by its GLDv2 ID. Returns True on success."""
    import urllib.request

    url_map = _load_landmark_url_map()
    url = url_map.get(img_id)
    if not url:
        return False
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PixelRAG-Bot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) >= 1000:
            with open(local_path, "wb") as out:
                out.write(data)
            return True
    except Exception as e:
        logger.debug(f"Download failed for landmark {img_id}: {e}")
    return False
