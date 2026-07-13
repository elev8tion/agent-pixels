class EVQANoRetrievalRetriever(BaseRetriever):
    """EVQA without retrieval: query + iNaturalist image only, no Wikipedia tiles.

    Used to test VLM's ability to answer from the species image alone.
    """

    def __init__(self, tiles_dir: str = "tiles/evqa"):
        self.tiles_dir = tiles_dir

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        inat_image_path = _get_query_image_path_for_example(example, self.tiles_dir)
        return RetrievalResult(
            images=[],
            retrieval_type="evqa_no_retrieval_multimodal",
            pixel_query_path=inat_image_path,
            query_image_path=inat_image_path,
        )
