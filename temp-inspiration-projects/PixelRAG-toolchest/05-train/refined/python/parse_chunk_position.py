def parse_chunk_position(chunk_path):
    """Extract (page, chunk_idx) from chunk path."""
    match = re.search(r"chunk_(\d+)_(\d+)\.png", chunk_path)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0
