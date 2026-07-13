def parse_chunk_pos(path):
    m = re.search(r"chunk_(\d+)_(\d+)\.png", path)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
