class MissingImageError(FileNotFoundError):
    """Raised when a referenced image path no longer exists on disk."""
