def compute_retrieval_metrics(q_embs, i_embs, gold_doc_indices):
    """Compute retrieval metrics for a query set against a larger document pool."""
    sims = q_embs @ i_embs.T  # (Q, M)
    gold_doc_indices = np.asarray(gold_doc_indices)
    rankings = (-sims).argsort(axis=1)
    ranks = np.argmax(rankings == gold_doc_indices[:, None], axis=1)
    pos_sims = sims[np.arange(sims.shape[0]), gold_doc_indices]

    if sims.shape[1] > 1:
        neg_sum = sims.sum(axis=1) - pos_sims
        mean_neg_per_query = neg_sum / (sims.shape[1] - 1)
        mean_neg_sim = float(mean_neg_per_query.mean())
        margin = float((pos_sims - mean_neg_per_query).mean())
    else:
        mean_neg_sim = 0.0
        margin = float(pos_sims.mean())

    return {
        "recall@1": float((ranks < 1).mean()),
        "recall@5": float((ranks < 5).mean()),
        "recall@10": float((ranks < 10).mean()),
        "mrr": float((1.0 / (ranks + 1)).mean()),
        "mean_pos_sim": float(pos_sims.mean()),
        "mean_neg_sim": mean_neg_sim,
        "margin": margin,
    }
