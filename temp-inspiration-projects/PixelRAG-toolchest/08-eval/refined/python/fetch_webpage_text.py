def fetch_webpage_text(url: str, max_chars: int = 50000) -> str | None:
    """Fetch webpage and extract clean text content using trafilatura.

    Args:
        url: URL to fetch.
        max_chars: Maximum characters to return.

    Returns:
        Extracted text content, or None if failed.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            logger.warning(f"Failed to download {url}")
            return None

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )

        if text is None:
            logger.warning(f"Failed to extract text from {url}")
            return None

        # Clean up excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Truncate if needed
        if max_chars and len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated]"

        return text
    except Exception as e:
        logger.warning(f"Fetch failed for {url}: {e}")
        return None
