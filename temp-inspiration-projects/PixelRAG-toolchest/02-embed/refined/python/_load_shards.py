def _load_shards(embeddings_dir: str):
    """Load and deduplicate all shard .npz files. Yields (embeddings, metadata) per shard."""
    emb_dir = Path(embeddings_dir)
    shard_files = sorted(emb_dir.glob("shard_*.npz"))
    print(f"Found {len(shard_files)} shard files in {embeddings_dir}")
    if not shard_files:
        print("No shard files found!", file=sys.stderr)
        sys.exit(1)
    return shard_files
