def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed tiles from a single shard using Qwen3-VL-Embedding-2B.",
    )
    parser.add_argument(
        "--shard-dir",
        required=True,
        help="Path to shard directory (e.g. output_coordinated/shard_042)",
    )
    parser.add_argument(
        "--output-dir", required=True, help="Output directory for .npz file"
    )
    parser.add_argument(
        "--gpu-ids",
        default="all",
        help="Comma-separated GPU IDs, or 'all' (default: all)",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen3-VL-Embedding-2B",
        help="Model name or path (default: Qwen/Qwen3-VL-Embedding-2B)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=128,
        help="Tiles per embed() call (default: 128)",
    )
    parser.add_argument(
        "--io-workers",
        type=int,
        default=8,
        help="Threads per GPU process for tile read/hash/decode (default: 8)",
    )
    parser.add_argument(
        "--compress-npz",
        action="store_true",
        help="Compress output npz files (smaller but slower)",
    )
    parser.add_argument(
        "--reuse-workers",
        action="store_true",
        help="Reuse persistent GPU workers across multiple embed_shard calls in-process",
    )
    parser.add_argument(
        "--backend",
        choices=["vllm", "sglang", "direct_gpu"],
        default="sglang",
        help="Embedding backend (default: sglang)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from checkpoint (skip already embedded articles)",
    )
    parser.add_argument(
        "--patch",
        action="store_true",
        help="Patch mode: diff hashes, re-embed only changed tiles",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="With --patch: only show diff, don't embed or write",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="With --patch: skip confirmation prompt",
    )
    parser.add_argument(
        "--hash-workers",
        type=int,
        default=32,
        help="Threads for parallel hashing in patch mode (default: 32)",
    )
    parser.add_argument(
        "--max-pixels",
        type=int,
        default=None,
        help="Max pixels per tile image before resize (e.g. 200000). "
        "Reduces visual tokens for faster inference. None = no resize.",
    )
    parser.add_argument(
        "--chunk-height",
        type=int,
        default=None,
        help="Split tall tiles into chunks of this height (e.g. 1024). "
        "Each chunk gets a separate embedding. None = no chunking.",
    )
    parser.add_argument(
        "--enforce-eager",
        action="store_true",
        help="Disable CUDA graph capture in vLLM (fixes hangs on some GPUs).",
    )
    parser.add_argument(
        "--redirects-json",
        default=None,
        help="Path to .redirects.json to skip redirect articles",
    )
    parser.add_argument(
        "--mode",
        choices=["chunks", "tiles"],
        default="chunks",
        help="Embedding unit: 'chunks' (1024px strips, default) or 'tiles' (full 8192px tiles)",
    )
    parser.add_argument(
        "--instruction",
        default=DEFAULT_INSTRUCTION,
        help="System prompt instruction for embedding (default: %(default)r)",
    )
    parser.add_argument(
        "--adapter",
        default=None,
        help="Path to PEFT LoRA adapter checkpoint directory. "
        "Loaded and merged into base model weights before embedding. "
        "Only supported with direct_gpu backend.",
    )
    return parser.parse_args()
