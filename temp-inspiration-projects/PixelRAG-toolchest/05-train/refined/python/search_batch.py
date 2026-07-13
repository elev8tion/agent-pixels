def search_batch(
    api_url: str, queries: list[str], n_docs: int, timeout: int = 300, retries: int = 5
) -> list[dict]:
    payload = {"queries": [{"text": q} for q in queries], "n_docs": n_docs}
    body = json.dumps(payload).encode()
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                api_url.rstrip("/") + "/search",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())["results"]
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            wait = 2**attempt
            print(
                f"  search_batch attempt {attempt + 1}/{retries} failed: {e}; retry in {wait}s",
                file=sys.stderr,
            )
            time.sleep(wait)
    raise RuntimeError(f"search_batch failed after {retries}: {last_err}")
