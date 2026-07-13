@dataclass
class RetrievalResult:
    """Result from a retrieval operation."""

    # Text content (for text-based retrieval)
    text: str | None = None

    # Image paths with scores (for vector retrieval)
    images: list[tuple[str, float]] = field(default_factory=list)

    # Per-image source URLs, aligned with ``images`` when provided.
    image_urls: list[str | None] = field(default_factory=list)

    # Base64 encoded image (for screenshot)
    base64_image: str | None = None

    # Source URL
    source_url: str | None = None

    # Which retrieval type was used
    retrieval_type: str = "naive"

    # Path to pixel query image used for retrieval embedding (rendered card or raw photo)
    pixel_query_path: str | None = None

    # Path to raw species/landmark photo for generation (always the original photo,
    # never the rendered card). If None, falls back to pixel_query_path in build_messages.
    query_image_path: str | None = None

    @property
    def has_content(self) -> bool:
        """Check if retrieval found any content."""
        return bool(self.text or self.images or self.base64_image)
