class ScreenshotRetriever(BaseRetriever):
    """Use screenshot that was prepared in data layer.

    Expects screenshot to be captured beforehand. This retriever just
    loads and encodes the existing screenshot.

    For ground truth evaluation, uses encode_screenshot_for_vlm_async which
    does NOT apply max_height limit. You can control max_pixels to study
    the effect of resize on VLM performance.

    Args:
        screenshot_dir: Directory containing screenshots.
        max_pixels: Maximum pixels before resize. If None, no resize (89M limit).
                    Common values:
                    - None: No resize (let VLM handle it)
                    - 16_777_216 (16M): Qwen3-VL default, ~16K tokens
                    - 4_000_000 (4M): ~4K tokens
                    - 1_000_000 (1M): ~1K tokens
    """

    def __init__(
        self, screenshot_dir: str = "screenshots", max_pixels: int | None = None
    ):
        self.screenshot_dir = screenshot_dir
        self.max_pixels = max_pixels

    async def retrieve(self, query: str, example: dict) -> RetrievalResult:
        from .simpleqa_data import (
            capture_screenshot_async,
            encode_screenshot_for_vlm_async,
            extract_url_from_metadata,
        )

        # Get or capture screenshot
        screenshot_path = await capture_screenshot_async(example, self.screenshot_dir)

        if not screenshot_path:
            return RetrievalResult(
                retrieval_type="screenshot",
                source_url=extract_url_from_metadata(example),
            )

        # Encode to base64 with configurable max_pixels
        base64_image = await encode_screenshot_for_vlm_async(
            screenshot_path, max_pixels=self.max_pixels
        )

        return RetrievalResult(
            base64_image=base64_image,
            source_url=extract_url_from_metadata(example),
            retrieval_type="screenshot",
        )
