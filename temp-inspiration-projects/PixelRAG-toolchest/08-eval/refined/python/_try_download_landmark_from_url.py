def _try_download_landmark_from_url(
    example_id: str, img_id: str, local_path: str
) -> bool:
    """Try to download landmark image from train.csv URL. Used when GLDv2 TARs unavailable.

    Returns True if download succeeded and file is valid, False otherwise.
    """
    import urllib.request

    train_csv = os.path.join(_LANDMARK_V2_DATA_DIR, "train.csv")
    if not os.path.exists(train_csv):
        return False
    import csv

    with open(train_csv) as f:
        for row in csv.DictReader(f):
            if row.get("id") == img_id:
                url = row.get("url", "")
                if url:
                    try:
                        req = urllib.request.Request(
                            url, headers={"User-Agent": "PixelRAG-Bot/1.0"}
                        )
                        with urllib.request.urlopen(req, timeout=30) as resp:
                            data = resp.read()
                        if len(data) >= 1000:
                            with open(local_path, "wb") as out:
                                out.write(data)
                            return True
                    except Exception as e:
                        logger.debug(
                            f"URL download failed for {example_id} (img_id={img_id}): {e}"
                        )
                return False
    return False
