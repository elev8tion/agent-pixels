@torch.no_grad()
def run_search_api_retrieval_eval(
    model, processor, examples, device, search_api_url, batch_size=32, n_docs=3
):
    """Compute exact-image Recall@1/3 against the full search datastore."""
    was_training = model.training
    model.eval()

    def _normalize_tile_path(path_str):
        """Normalize tile path for matching.

        Absolute paths are used as-is. Relative paths starting with 'images/'
        (from HF dataset) are matched by shard suffix for backward compatibility
        with search APIs that return absolute paths.
        """
        p = Path(path_str)
        if p.is_absolute():
            return str(p)
        # Relative path (e.g. images/shard_XXX/...) — extract shard suffix
        parts = p.parts
        for i, part in enumerate(parts):
            if part.startswith("shard_"):
                return "/".join(parts[i:])
        return path_str

    def _match_paths(gold, hit):
        """Check if gold and hit refer to the same tile."""
        if gold == hit:
            return True
        # Fallback: compare shard suffixes
        g_parts = Path(gold).parts
        h_parts = Path(hit).parts
        for gi, gp in enumerate(g_parts):
            if gp.startswith("shard_"):
                g_suffix = "/".join(g_parts[gi:])
                for hi, hp in enumerate(h_parts):
                    if hp.startswith("shard_"):
                        return g_suffix == "/".join(h_parts[hi:])
        return False

    recall1 = 0
    recall3 = 0
    total = 0
    for i in range(0, len(examples), batch_size):
        batch = examples[i : i + batch_size]
        queries = [item["query"] for item in batch]
        gold_paths = [_normalize_tile_path(item["gold_path"]) for item in batch]
        query_embs = embed_query_texts(
            model, processor, queries, device, batch_size=batch_size
        )
        search_resp = search_api_by_embeddings(
            search_api_url, query_embs, n_docs=n_docs
        )
        for gold_path, result in zip(gold_paths, search_resp["results"]):
            hit_paths = [hit["path"] for hit in result["hits"]]
            total += 1
            if hit_paths and _match_paths(gold_path, hit_paths[0]):
                recall1 += 1
            if any(_match_paths(gold_path, hp) for hp in hit_paths[:3]):
                recall3 += 1

    if was_training:
        model.train()
    if total == 0:
        return {"recall@1": 0.0, "recall@3": 0.0}
    return {
        "recall@1": recall1 / total,
        "recall@3": recall3 / total,
    }
