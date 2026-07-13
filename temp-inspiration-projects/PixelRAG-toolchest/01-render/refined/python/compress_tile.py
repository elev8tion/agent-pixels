def compress_tile(raw_path: str, out_path: str, quality: int = 85) -> None:
    """Read raw BGRA file, compress to JPEG, delete raw file.

    Raw file layout (written by Chrome rawFilePath):
        bytes 0-3:  width  (uint32 LE)
        bytes 4-7:  height (uint32 LE)
        bytes 8-11: rowBytes (uint32 LE)
        bytes 12+:  BGRA pixels
    """
    from PIL import Image

    data = open(raw_path, "rb").read()
    w, h, rb = struct.unpack_from("<III", data, 0)
    img = Image.frombuffer("RGBA", (w, h), data[12:], "raw", "BGRA", rb, 1)
    img = img.convert("RGB")
    img.save(out_path, "JPEG", quality=quality)
    os.unlink(raw_path)
