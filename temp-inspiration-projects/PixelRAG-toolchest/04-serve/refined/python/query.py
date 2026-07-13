class Query(BaseModel):
    text: str | None = None
    image: str | None = None  # base64-encoded image
    embedding: list[float] | None = None  # pre-computed query embedding
