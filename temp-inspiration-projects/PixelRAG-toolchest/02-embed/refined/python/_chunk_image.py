def _chunk_image(img: "Image.Image", chunk_height: int) -> list["Image.Image"]:
    """Split a tall image into horizontal strips of chunk_height pixels.

    The last chunk is merged into the previous one if it would be shorter
    than _MIN_CHUNK_HEIGHT pixels.
    """
    w, h = img.size
    if h <= chunk_height:
        return [img]
    chunks = []
    for y in range(0, h, chunk_height):
        y_end = min(y + chunk_height, h)
        # Merge tiny remainder into previous chunk
        if y_end - y < _MIN_CHUNK_HEIGHT and chunks:
            prev = chunks[-1]
            merged = Image.new("RGB", (w, prev.size[1] + y_end - y))
            merged.paste(prev, (0, 0))
            merged.paste(img.crop((0, y, w, y_end)), (0, prev.size[1]))
            chunks[-1] = merged
        else:
            chunks.append(img.crop((0, y, w, y_end)))
    return chunks
