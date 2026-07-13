def decode_tile(tc: TileCapture) -> Image.Image | None:
    try:
        if tc.raw_file_path and os.path.exists(tc.raw_file_path):
            data = open(tc.raw_file_path, "rb").read()
            w, h, rb = struct.unpack_from("<III", data, 0)
            img = Image.frombuffer(
                "RGBA", (w, h), data[12:], "raw", "BGRA", rb, 1
            ).convert("RGB")
            return img
        elif tc.image_bytes:
            return Image.open(io.BytesIO(tc.image_bytes)).convert("RGB")
    except Exception:
        return None
    return None
