def make_rank_data(processor, batch_size, device, rank):
    """Create per-rank fake data (different data on each rank)."""
    from PIL import Image
    import numpy as np

    # Different seed per rank → different data
    rng = np.random.RandomState(1000 + rank)
    queries = [f"Rank {rank} query about topic {i}" for i in range(batch_size)]
    images = []
    for i in range(batch_size):
        arr = rng.randint(0, 255, (200, 300, 3), dtype=np.uint8)
        images.append(Image.fromarray(arr))

    from train_contrastors import process_queries, process_doc_images

    query_inputs = process_queries(processor, queries)
    doc_inputs = process_doc_images(processor, images)

    query_inputs = {k: v.to(device) for k, v in query_inputs.items()}
    doc_inputs = {k: v.to(device) for k, v in doc_inputs.items()}
    return query_inputs, doc_inputs
