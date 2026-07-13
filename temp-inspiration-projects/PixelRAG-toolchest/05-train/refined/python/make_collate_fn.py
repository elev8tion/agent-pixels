def make_collate_fn(processor, num_hard_negatives=0):
    """Collate: process queries as text, images as visual prompts.

    With hard negatives, document images are interleaved:
        [pos1, neg1a, neg1b, pos2, neg2a, neg2b, ...]
    so that document.size(0) = batch_size * (1 + num_hard_negatives).
    """

    def _load_image(path):
        with Image.open(path) as im:
            return im.convert("RGB")

    def collate(batch):
        t_start = time.time()
        queries = [item[0] for item in batch]

        # Build document image list: positive + hard negatives per query
        doc_images = []
        for item in batch:
            pos_path = item[1]
            doc_images.append(_load_image(pos_path))
            neg_paths = item[2] if len(item) > 2 else []
            for np_ in neg_paths:
                if np_ is not None:
                    doc_images.append(_load_image(np_))
                else:
                    doc_images.append(_load_image(pos_path))
        t_io = time.time()

        query_inputs = process_queries(processor, list(queries))
        t_q = time.time()
        image_inputs = process_doc_images(processor, doc_images)
        t_d = time.time()
        total = t_d - t_start
        if total > 5:
            logger.warning(
                f"Slow collate: io={t_io - t_start:.1f}s q={t_q - t_io:.1f}s "
                f"img={t_d - t_q:.1f}s total={total:.1f}s"
            )
        return query_inputs, image_inputs

    return collate
