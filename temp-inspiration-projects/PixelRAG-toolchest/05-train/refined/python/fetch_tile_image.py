def fetch_tile_image(search_api_url, path, timeout=30, retries=3):
    """Fetch a tile image via the search API's /tile endpoint.

    Falls back to local file if the path exists locally.
    Retries on network errors with exponential backoff.
    """
    if os.path.exists(path):
        return Image.open(path)
    tile_url = (
        search_api_url.rstrip("/") + "/tile?" + urllib.parse.urlencode({"path": path})
    )
    for attempt in range(retries):
        try:
            req = urlrequest.Request(tile_url, method="GET")
            with urlrequest.urlopen(req, timeout=timeout) as resp:
                return Image.open(io.BytesIO(resp.read()))
        except (TimeoutError, OSError) as e:
            if attempt < retries - 1:
                wait = 2**attempt
                logger.warning(
                    f"fetch_tile_image attempt {attempt + 1}/{retries} failed for {path}: {e}, retrying in {wait}s"
                )
                time.sleep(wait)
            else:
                raise
