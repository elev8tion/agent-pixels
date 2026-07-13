def fetch_tile(
    api_url: str, path: str, dst: Path, timeout: int = 60, retries: int = 3
) -> tuple[bool, str]:
    url = api_url.rstrip("/") + "/tile?" + urllib.parse.urlencode({"path": path})
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            dst.parent.mkdir(parents=True, exist_ok=True)
            tmp = dst.with_suffix(dst.suffix + ".tmp")
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dst)
            return True, ""
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as e:
            last_err = str(e)
            if attempt < retries - 1:
                time.sleep(2**attempt)
    return False, f"{last_err}"
