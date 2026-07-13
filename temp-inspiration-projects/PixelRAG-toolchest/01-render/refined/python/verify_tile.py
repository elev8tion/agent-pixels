def verify_tile(
    captured: Image.Image, gt_path: Path, is_lossy: bool
) -> tuple[bool, float]:
    gt = Image.open(gt_path).convert("RGB")
    cap_arr = np.array(captured, dtype=np.float32)
    gt_arr = np.array(gt, dtype=np.float32)
    if cap_arr.shape != gt_arr.shape:
        return False, 999.0
    diff = np.abs(cap_arr - gt_arr)
    mean_diff = float(diff.mean())
    threshold = JPEG_MAX_MEAN_DIFF if is_lossy else LOSSLESS_MAX_MEAN_DIFF
    return mean_diff <= threshold, mean_diff
