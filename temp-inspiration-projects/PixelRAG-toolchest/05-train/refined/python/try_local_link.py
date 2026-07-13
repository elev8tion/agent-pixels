def try_local_link(suffix: str, local_root: Path, mirror_root: Path) -> bool:
    """If local_root/images/<suffix> exists, hardlink it into mirror_root/<suffix>.
    Returns True on success."""
    src = local_root / "images" / suffix
    if not src.exists():
        return False
    dst = mirror_root / suffix
    if dst.exists():
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except OSError:
        # cross-device; fall back to copy (only expected when local & mirror are on different filesystems)
        import shutil

        shutil.copy2(src, dst)
    return True
