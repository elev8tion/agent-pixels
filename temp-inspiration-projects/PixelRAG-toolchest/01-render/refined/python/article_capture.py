@dataclass
class ArticleCapture:
    """Raw capture results for all tiles of one article."""

    article_path: str
    tiles: list[TileCapture] = field(default_factory=list)
    page_height: int = 0
    n_tiles_expected: int = 0
    total_shot_ms: float = 0.0
    total_nav_ms: float = 0.0
    sem_wait_ms: float = 0.0
    errors: list[str] = field(default_factory=list)
