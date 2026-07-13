def build_ivf(
    embeddings_dir: str,
    output_dir: str,
    nlist: int = 4096,
    nprobe: int = 128,
    train_sample: int = 500_000,
    metric: str = "ip",
    gpu_id: int = -1,
):
    """Build FAISS IVFFlat index.

    Args:
        nlist: number of IVF clusters (default 4096, good for ~30M vectors)
        nprobe: default search nprobe stored in the index
        train_sample: number of vectors to sample for K-means training
        metric: 'ip' (inner product / cosine for L2-normalized vectors) or 'l2'
        gpu_id: GPU to use for training (-1 = CPU only)
    """
    import faiss

    # Use all cores for FAISS CPU operations
    faiss.omp_set_num_threads(os.cpu_count())

    os.makedirs(output_dir, exist_ok=True)

    shard_files = _load_shards(embeddings_dir)

    print("\nMerging and deduplicating shards...")
    merged = _merge_all_shards(shard_files)
    embeddings = merged["embeddings"]
    dim = merged["dim"]
    n = embeddings.shape[0]
    print(f"Final: {n:,} × {dim}")

    # Save metadata
    metadata_path = os.path.join(output_dir, "metadata.npz")
    print(f"Saving metadata to {metadata_path}...")
    np.savez(
        metadata_path,
        article_ids=merged["article_ids"],
        tile_indices=merged["tile_indices"],
        chunk_indices=merged["chunk_indices"],
        y_offsets=merged["y_offsets"],
        tile_heights=merged["tile_heights"],
    )

    # Build IVF index
    metric_type = faiss.METRIC_INNER_PRODUCT if metric == "ip" else faiss.METRIC_L2

    # Train on a sample
    actual_train = min(train_sample, n)
    train_indices = np.random.choice(n, actual_train, replace=False)
    train_data = embeddings[train_indices]

    quantizer = faiss.IndexFlatIP(dim) if metric == "ip" else faiss.IndexFlatL2(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist, metric_type)

    if gpu_id >= 0:
        # GPU-accelerated training: move CPU index to GPU, train, move back
        print(
            f"\nTraining IVF on GPU {gpu_id} (nlist={nlist}) on {actual_train:,} vectors..."
        )
        t0 = time.time()
        res = faiss.StandardGpuResources()
        gpu_index = faiss.index_cpu_to_gpu(res, gpu_id, index)
        gpu_index.train(train_data)
        print(f"GPU training done in {time.time() - t0:.1f}s")

        # Copy trained state back to CPU index
        print("Copying trained index to CPU...")
        index = faiss.index_gpu_to_cpu(gpu_index)
        del gpu_index, res  # free GPU memory
    else:
        # CPU training
        print(f"\nTraining IVF on CPU (nlist={nlist}) on {actual_train:,} vectors...")
        t0 = time.time()
        index.train(train_data)
        print(f"CPU training done in {time.time() - t0:.1f}s")

    # Add all vectors (CPU — GPU VRAM can't hold 30M × 2048)
    print(f"Adding {n:,} vectors...")
    t0 = time.time()
    batch = 100_000
    for start in range(0, n, batch):
        end = min(start + batch, n)
        index.add(embeddings[start:end])
        elapsed = time.time() - t0
        rate = end / elapsed if elapsed > 0 else 0
        eta = (n - end) / rate if rate > 0 else 0
        print(
            f"  added {end:,}/{n:,} ({elapsed:.0f}s, {rate:.0f} vec/s, ETA {eta:.0f}s)"
        )
    print(f"Add done in {time.time() - t0:.1f}s")

    # Set default nprobe
    index.nprobe = nprobe

    # Save
    index_path = os.path.join(output_dir, "index.faiss")
    print(f"Saving index to {index_path}...")
    faiss.write_index(index, index_path)

    # Summary
    summary = {
        "backend": "ivf",
        "total_vectors": n,
        "dimension": dim,
        "nlist": nlist,
        "nprobe": nprobe,
        "metric": metric,
        "index_file": index_path,
        "metadata_file": metadata_path,
    }
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    index_size = os.path.getsize(index_path)
    print(
        f"\nDone! Index: {index_size / 1e9:.1f} GB, metadata: {os.path.getsize(metadata_path) / 1e9:.1f} GB"
    )
    print(f"Summary: {summary_path}")
