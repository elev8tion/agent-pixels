def pack_one_shard(shard_dir: Path, tar_path: Path, output_root: Path) -> int:
    file_count = 0
    tar_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, mode="w") as tar:
        for path in sorted(shard_dir.rglob("*")):
            if not path.is_file():
                continue
            arcname = path.relative_to(output_root).as_posix()
            tar.add(path, arcname=arcname, recursive=False)
            file_count += 1
    return file_count
