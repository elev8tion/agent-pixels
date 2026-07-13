def search(query: str, port: int) -> list[dict]:
    body = json.dumps({"queries": [{"text": query}], "n_docs": 5}).encode()
    req = urllib.request.Request(
        f"http://localhost:{port}/search",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get("results", [{}])[0].get("hits", [])
