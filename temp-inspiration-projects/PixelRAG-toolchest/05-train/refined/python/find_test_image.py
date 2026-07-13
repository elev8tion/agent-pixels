def find_test_image():
    """Find any valid chunk image for testing."""
    data_file = "data/train.jsonl"
    if not os.path.exists(data_file):
        data_file = "data/train_hn.jsonl"
    with open(data_file) as f:
        for line in f:
            item = json.loads(line)
            path = item["chunk_path"]
            if os.path.exists(path):
                return path
    raise RuntimeError("No valid test image found")
