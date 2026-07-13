def validate_gt(ground_truth: dict[str, list[Path]]) -> tuple[int, int, list[str]]:
    """Validate GT tiles are non-degenerate (not blank, not tiny, readable).

    Returns (ok, bad, bad_examples).
    """
    ok = 0
    bad = 0
    examples = []
    for article_path, tile_paths in ground_truth.items():
        for tp in tile_paths:
            try:
                img = Image.open(tp)
                arr = np.array(img)
                if arr.std() < 1.0:
                    bad += 1
                    if len(examples) < 10:
                        examples.append(
                            f"{article_path} {tp.name}: blank (std={arr.std():.1f})"
                        )
                    continue
                ok += 1
            except Exception as e:
                bad += 1
                if len(examples) < 10:
                    examples.append(f"{article_path} {tp.name}: {e}")
    return ok, bad, examples
