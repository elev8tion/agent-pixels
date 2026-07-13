def build_ground_truth(task: str, original_data: dict) -> str:
    """Match evaluate.py convert_to_evaluate_format."""
    if task == "encyclopedic_vqa":
        refs = original_data.get("reference_list") or []
        if refs:
            return "Any of: " + " | ".join(refs)
        return original_data.get("answer", "") or original_data.get("gt_answer", "")
    # mmsearch / worldvqa / simplevqa / factualvqa
    return original_data.get("gt_answer", "") or original_data.get("answer", "")
