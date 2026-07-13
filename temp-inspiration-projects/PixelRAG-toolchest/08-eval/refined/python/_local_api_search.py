async def _local_api_search(
    api_url: str, query_text: str, top_k: int, nprobe: int | None = None
) -> list[dict]:
    """Single-query search against local API, returns hits."""
    import aiohttp

    payload = {"queries": [{"text": query_text}], "n_docs": top_k}
    if nprobe is not None:
        payload["nprobe"] = nprobe
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300),
            ) as response:
                if response.status != 200:
                    return []
                result = await response.json()
                results_list = result.get("results", [])
                return results_list[0].get("hits", []) if results_list else []
    except Exception as e:
        logger.error(f"ReAct search failed: {e}")
        return []
