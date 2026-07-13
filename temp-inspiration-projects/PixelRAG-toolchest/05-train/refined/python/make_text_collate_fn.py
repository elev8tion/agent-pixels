def make_text_collate_fn(processor, num_hard_negatives=0):
    """Collate for text-only training: queries and doc texts both as text."""

    def collate(batch):
        queries = [item[0] for item in batch]
        doc_texts = []
        for item in batch:
            doc_texts.append(item[1])  # positive passage
            neg_texts = item[2] if len(item) > 2 else []
            for nt in neg_texts:
                doc_texts.append(nt)

        query_inputs = process_queries(processor, list(queries))
        doc_inputs = process_doc_texts(processor, doc_texts)
        return query_inputs, doc_inputs

    return collate
