class StatusResponse(BaseModel):
    total_vectors: int
    dimension: int
    nlist: int
    nprobe: int
    model: str
    index_dir: str = ""
    tiles_dir: str = ""
    index_built_at: str
    index_size_bytes: int
    metadata_size_bytes: int
