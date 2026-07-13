def test_search(index_dir: str, nprobe: int = 128, k: int = 10):
    """Test search on a built IVF index."""
    import faiss

    index_path = os.path.join(index_dir, "index.faiss")
    metadata_path = os.path.join(index_dir, "metadata.npz")

    print(f"Loading index from {index_path}...")
    t0 = time.time()
    index = faiss.read_index(index_path)
    print(f"Loaded in {time.time() - t0:.1f}s: {index.ntotal:,} vectors")

    index.nprobe = nprobe
    print(f"nprobe={nprobe}")

    # Load metadata
    meta = np.load(metadata_path)
    article_ids = meta["article_ids"]

    # Self-search: query with first vector
    # Extract first vector from the index
    query = index.reconstruct(0).reshape(1, -1)
    print("Query: first vector (self-search, should return itself as #1)")

    t0 = time.time()
    distances, indices = index.search(query, k)
    dt = time.time() - t0

    print(f"\nTop-{k} results ({dt * 1000:.1f}ms):")
    for i in range(k):
        idx = indices[0, i]
        dist = distances[0, i]
        aid = article_ids[idx]
        print(f"  {i + 1}. row={idx}, dist={dist:.6f}, article_id={aid}")
