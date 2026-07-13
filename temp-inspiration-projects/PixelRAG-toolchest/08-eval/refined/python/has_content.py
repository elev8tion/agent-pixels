@property
    def has_content(self) -> bool:
        """Check if retrieval found any content."""
        return bool(self.text or self.images or self.base64_image)
