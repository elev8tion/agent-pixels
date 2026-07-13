def convert_line(item):
    """Convert one data item from contrastors format to swift format."""
    query = item["query"]
    pos_path = item["chunk_path"]

    if not os.path.exists(pos_path):
        return None

    doc_messages = [
        {"role": "system", "content": DOC_INSTRUCTION},
        {"role": "user", "content": "<image>"},
    ]

    out = {
        "messages": [
            {"role": "system", "content": QUERY_INSTRUCTION},
            {"role": "user", "content": query},
        ],
        "positive_messages": [doc_messages],
        "positive_images": [[pos_path]],
    }

    neg_paths = item.get("neg_chunk_paths", [])
    if neg_paths:
        neg_messages = []
        neg_images = []
        for np_ in neg_paths:
            if np_ and os.path.exists(np_):
                neg_messages.append(doc_messages)
                neg_images.append([np_])
        if neg_messages:
            out["negative_messages"] = neg_messages
            out["negative_images"] = neg_images

    return out
