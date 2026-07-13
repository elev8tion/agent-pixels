def load(args):
    """Load index, metadata, model, and articles.json."""
    import torch

    device = args.device
    dtype = torch.float32 if device == "cpu" else torch.bfloat16

    # Load FAISS index
    index_path = os.path.join(args.index_dir, "index.faiss")
    logger.info("Loading FAISS index from %s...", index_path)
    t0 = time.time()
    index = faiss.read_index(index_path)
    logger.info("Loaded index: %d vectors in %.1fs", index.ntotal, time.time() - t0)

    # Load metadata
    metadata_path = os.path.join(args.index_dir, "metadata.npz")
    logger.info("Loading metadata from %s...", metadata_path)
    meta = np.load(metadata_path)

    # Load summary
    summary_path = os.path.join(args.index_dir, "summary.json")
    summary = {}
    if os.path.exists(summary_path):
        with open(summary_path) as f:
            summary = json.load(f)

    # Load articles.json
    logger.info("Loading articles.json from %s...", args.articles_json)
    with open(args.articles_json) as f:
        articles = json.load(f)
    logger.info("Loaded %d article slugs", len(articles))

    # Load embedding model
    from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

    logger.info("Loading model %s on device=%s dtype=%s...", args.model, device, dtype)
    processor = AutoProcessor.from_pretrained(args.model, trust_remote_code=True)
    model = Qwen3VLForConditionalGeneration.from_pretrained(
        args.model,
        trust_remote_code=True,
        dtype=dtype,
    )
    adapter_path = getattr(args, "peft_adapter", None)
    if adapter_path:
        from peft import PeftModel

        logger.info("Loading LoRA adapter from %s...", adapter_path)
        model = PeftModel.from_pretrained(model, adapter_path)
        model = model.merge_and_unload()
        logger.info("LoRA adapter merged")
    model = model.to(device).eval()
    logger.info("Model loaded")

    # File sizes
    index_size = os.path.getsize(index_path)
    meta_size = os.path.getsize(metadata_path)

    # Index build time from file mtime
    index_mtime = os.path.getmtime(index_path)
    index_built_at = datetime.fromtimestamp(index_mtime, tz=timezone.utc).isoformat()

    _state.update(
        {
            "index": index,
            "metadata": meta,
            "articles": articles,
            "processor": processor,
            "model": model,
            "device": device,
            "model_name": args.model,
            "index_dir": args.index_dir,
            "tiles_dir": args.tiles_dir,
            "dimension": summary.get("dimension", index.d),
            "nlist": summary.get("nlist", 4096),
            "index_built_at": index_built_at,
            "index_size_bytes": index_size,
            "metadata_size_bytes": meta_size,
            "ondemand": None,
        }
    )

    # Optional: render tile images on demand from a kiwix ZIM instead of reading a
    # materialized (multi-TB) tiles/ dir. Only retrieved pages get rendered + cached.
    if getattr(args, "render_on_demand", False):
        from .render_ondemand import OnDemandTiles

        book = args.zim_book or _derive_kiwix_book(args.kiwix_url)
        if not book:
            logger.warning(
                "render-on-demand: could not derive kiwix book from %s "
                "(pass --zim-book)",
                args.kiwix_url,
            )
        cache = os.path.join(args.tiles_dir or "./tiles_cache", "_ondemand")
        _state["ondemand"] = OnDemandTiles(args.kiwix_url, book, cache)
        logger.info(
            "On-demand tile rendering enabled (kiwix=%s book=%s cache=%s)",
            args.kiwix_url,
            book,
            cache,
        )
