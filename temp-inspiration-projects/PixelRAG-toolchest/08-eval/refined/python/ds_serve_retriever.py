class DsServeRetriever(BaseRetriever):
    """Use ds-serve API for external text augmentation.

    Calls ds-serve search API to retrieve relevant text passages for the query.
    """

    def __init__(
        self, api_url: str = "http://api.ds-serve.org:30888/search", top_k: int = 3
    ):
        self.api_url = api_url
        self.top_k = top_k

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        import aiohttp
        import asyncio

        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = {"Content-Type": "application/json"}
                payload = {"query": query}

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        if response.status == 200:
                            result = await response.json()

                            # Extract passages from response
                            passages = []
                            if "results" in result and "passages" in result["results"]:
                                # passages is a list of lists, get the first list
                                passage_list = (
                                    result["results"]["passages"][0]
                                    if result["results"]["passages"]
                                    else []
                                )

                                # Take top_k passages
                                for i, passage_data in enumerate(
                                    passage_list[: self.top_k]
                                ):
                                    if isinstance(passage_data, dict):
                                        text = passage_data.get(
                                            "text", ""
                                        ) or passage_data.get("center_text", "")
                                        if text:
                                            passages.append(text)

                            # Combine passages into context text
                            if passages:
                                combined_text = "\n\n".join(
                                    [
                                        f"[Passage {i + 1}]\n{text}"
                                        for i, text in enumerate(passages)
                                    ]
                                )

                                return RetrievalResult(
                                    text=combined_text,
                                    source_url=f"ds-serve:{self.api_url}",
                                    retrieval_type="ds_serve",
                                )
                            else:
                                return RetrievalResult(
                                    text="No passages found from ds-serve.",
                                    source_url=f"ds-serve:{self.api_url}",
                                    retrieval_type="ds_serve",
                                )
                        elif response.status == 429:
                            if attempt < max_retries - 1:
                                wait_time = min(2**attempt * 2, 10)
                                logger.warning(
                                    f"Rate limited (429), waiting {wait_time}s before retry ({attempt + 1}/{max_retries})"
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                error_msg = f"ds-serve API rate limited after {max_retries} retries"
                                logger.error(error_msg)
                                return RetrievalResult(
                                    text=error_msg, retrieval_type="ds_serve"
                                )
                        else:
                            error_text = await response.text()
                            error_msg = f"ds-serve API error: {response.status} - {error_text[:200]}"
                            logger.error(error_msg)
                            return RetrievalResult(
                                text=error_msg, retrieval_type="ds_serve"
                            )
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = min(2**attempt, 5)
                    logger.warning(
                        f"Timeout, waiting {wait_time}s before retry ({attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    error_msg = f"ds-serve API timeout after {max_retries} retries"
                    logger.error(error_msg)
                    return RetrievalResult(text=error_msg, retrieval_type="ds_serve")
            except Exception as e:
                error_msg = f"ds-serve API call failed: {e}"
                logger.error(error_msg)
                return RetrievalResult(text=error_msg, retrieval_type="ds_serve")

        return RetrievalResult(
            text="ds-serve API call failed after all retries", retrieval_type="ds_serve"
        )
