class WorldVQANoRetrievalRetriever(BaseRetriever):
    """WorldVQA without retrieval: query + image from dataset only.

    WorldVQA images are embedded in the HuggingFace dataset (PIL or base64).
    """

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        img = example.get("image")
        base64_img = _worldvqa_image_to_base64(img)
        return RetrievalResult(
            base64_image=base64_img,
            retrieval_type="worldvqa_no_retrieval",
        )
