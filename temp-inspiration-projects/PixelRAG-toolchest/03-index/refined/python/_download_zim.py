@staticmethod
    def _download_zim(url: str, dest: Path) -> Path:
        import urllib.request

        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".zim.part")
        logger.info("Downloading: %s", url)

        resp = urllib.request.urlopen(url)
        total = int(resp.headers.get("Content-Length", 0))

        from tqdm import tqdm

        with (
            open(tmp, "wb") as f,
            tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=dest.name,
                ncols=80,
            ) as bar,
        ):
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
                bar.update(len(chunk))

        tmp.rename(dest)
        logger.info("Saved: %s (%.0f MB)", dest, dest.stat().st_size / 1e6)
        return dest
