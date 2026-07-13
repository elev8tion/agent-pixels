def transform_rows(
    split_name: str,
    rows: list[dict],
    image_root: Path,
    images_dir: Path,
    link_mode: str,
) -> tuple[list[dict], dict]:
    out_rows = []
    unique_images = set()
    total_negatives = 0

    for row in rows:
        pos_rel = to_relative_image_path(row["chunk_path"], image_root)
        pos_src = Path(row["chunk_path"])
        materialize_image(pos_src, images_dir / pos_rel, link_mode)
        unique_images.add(pos_rel)

        neg_rel_paths = []
        for neg_path in row.get("neg_chunk_paths", []):
            neg_rel = to_relative_image_path(neg_path, image_root)
            materialize_image(Path(neg_path), images_dir / neg_rel, link_mode)
            unique_images.add(neg_rel)
            neg_rel_paths.append(f"images/{neg_rel}")
        total_negatives += len(neg_rel_paths)

        out_rows.append(
            {
                "query": row["query"],
                "chunk_path": f"images/{pos_rel}",
                "neg_chunk_paths": neg_rel_paths,
                "split": split_name,
            }
        )

    stats = {
        "rows": len(out_rows),
        "unique_images_referenced": len(unique_images),
        "avg_negatives_per_row": (total_negatives / len(out_rows)) if out_rows else 0.0,
    }
    return out_rows, stats
