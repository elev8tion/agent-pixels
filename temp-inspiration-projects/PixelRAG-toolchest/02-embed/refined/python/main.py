def main():
    parser = argparse.ArgumentParser(
        description="Build vector search index from wiki-screenshot embeddings"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = sub.add_parser("build", help="Build IVF index (default)")
    p_build.add_argument("--embeddings-dir", default="./data/embeddings")
    p_build.add_argument("--output-dir", default="./output/search_index")
    p_build.add_argument(
        "--nlist", type=int, default=4096, help="Number of IVF clusters (default: 4096)"
    )
    p_build.add_argument(
        "--nprobe",
        type=int,
        default=128,
        help="Default nprobe for search (default: 128)",
    )
    p_build.add_argument(
        "--train-sample",
        type=int,
        default=500_000,
        help="Vectors to sample for training (default: 500k)",
    )
    p_build.add_argument(
        "--metric",
        choices=["ip", "l2"],
        default="ip",
        help="Distance metric (default: ip for cosine/L2-normalized)",
    )
    p_build.add_argument(
        "--gpu-id",
        type=int,
        default=-1,
        help="GPU for K-means training (-1 = CPU only)",
    )

    # test
    p_test = sub.add_parser("test", help="Test search on built index")
    p_test.add_argument("--index-dir", default="./output/search_index")
    p_test.add_argument("--nprobe", type=int, default=128)
    p_test.add_argument("-k", type=int, default=10)

    args = parser.parse_args()

    if args.command == "build":
        build_ivf(
            args.embeddings_dir,
            args.output_dir,
            nlist=args.nlist,
            nprobe=args.nprobe,
            train_sample=args.train_sample,
            metric=args.metric,
            gpu_id=args.gpu_id,
        )
    elif args.command == "test":
        test_search(args.index_dir, nprobe=args.nprobe, k=args.k)
