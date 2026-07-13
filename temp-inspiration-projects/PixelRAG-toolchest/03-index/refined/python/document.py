@dataclass
class Document:
    id: str
    url: str | None = None
    path: str | None = None
    metadata: dict = field(default_factory=dict)
