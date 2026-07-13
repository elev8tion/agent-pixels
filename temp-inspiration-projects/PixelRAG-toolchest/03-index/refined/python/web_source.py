class WebSource(Source):
    """Source that reads URLs from a plain-text file (one per line).

    Args:
        urls_file: Path to a text file with one URL per line.
        preset: Optional preset name (e.g. "news") to load default config.
        **kwargs: Ignored (for forward compatibility).
    """

    def __init__(
        self,
        urls_file: str | None = None,
        preset: str | None = None,
        **kwargs,
    ):
        self.preset_config = PRESETS.get(preset, {}) if preset else {}
        self._urls: list[str] = []

        if urls_file:
            p = Path(urls_file)
            if p.exists():
                with open(p) as f:
                    self._urls = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
            else:
                raise FileNotFoundError(f"urls_file not found: {urls_file}")

    def __iter__(self) -> Iterator[Document]:
        for i, url in enumerate(self._urls):
            yield Document(
                id=f"web_{i:06d}",
                url=url,
                metadata={"type": "web", "source_url": url},
            )

    def __len__(self) -> int:
        return len(self._urls)
