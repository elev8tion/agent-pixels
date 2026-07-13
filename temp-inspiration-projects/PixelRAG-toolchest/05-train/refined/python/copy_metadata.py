def copy_metadata(source_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(source_dir.iterdir()):
        if src.name == "images":
            continue
        if src.is_file():
            shutil.copy2(src, output_dir / src.name)
