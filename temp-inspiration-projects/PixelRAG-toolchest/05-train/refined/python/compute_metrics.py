def compute_metrics(q_embs, i_embs):
    """Compute retrieval metrics. Each query[i] matches image[i]."""
    # Cosine similarity matrix (already L2 normalized by model)
    sims = q_embs @ i_embs.T  # (N, N)
    n = sims.shape[0]

    # Per-query: positive sim vs mean negative sim
    pos_sims = np.diag(sims)
    # Mask out diagonal for negative sims
    mask = ~np.eye(n, dtype=bool)
    neg_sims = sims[mask].reshape(n, n - 1)
    mean_neg_sims = neg_sims.mean(axis=1)
    max_neg_sims = neg_sims.max(axis=1)

    # Recall@K
    rankings = (-sims).argsort(axis=1)
    correct = np.arange(n)
    ranks = np.array([np.where(rankings[i] == correct[i])[0][0] for i in range(n)])

    recall_1 = (ranks < 1).mean()
    recall_5 = (ranks < 5).mean()
    recall_10 = (ranks < 10).mean()
    mrr = (1.0 / (ranks + 1)).mean()

    return {
        "mean_pos_sim": float(pos_sims.mean()),
        "mean_neg_sim": float(mean_neg_sims.mean()),
        "mean_max_neg_sim": float(max_neg_sims.mean()),
        "margin": float((pos_sims - mean_neg_sims).mean()),
        "recall@1": float(recall_1),
        "recall@5": float(recall_5),
        "recall@10": float(recall_10),
        "mrr": float(mrr),
    }
