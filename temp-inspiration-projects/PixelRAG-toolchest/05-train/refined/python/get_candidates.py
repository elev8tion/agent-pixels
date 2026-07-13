def get_candidates(item: dict, candidate_k: int) -> list[dict]:
    positive_key = (item["article_id"], item["chunk_index"])
    out = []
    for cand in item.get("retrieve_top20", []):
        cand_key = (cand.get("article_id"), cand.get("chunk_index"))
        if cand_key == positive_key:
            continue
        out.append(cand)
        if len(out) >= candidate_k:
            break
    return out
