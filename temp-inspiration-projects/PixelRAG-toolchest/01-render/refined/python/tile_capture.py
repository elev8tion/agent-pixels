@dataclass
class TileCapture:
    """Raw capture result for one tile. Decoded later during verification."""

    image_bytes: bytes | None = None
    raw_file_path: str | None = None

    shot_ms: float = 0.0
    nav_ms: float = 0.0
    tile_index: int = 0
    clip_y: int = 0
    clip_h: int = 0
