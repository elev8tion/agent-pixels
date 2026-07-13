def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--miniv8-json", type=Path, default=DEFAULT_MINIV8_JSON)
    parser.add_argument("--tiles-dir", type=Path, default=DEFAULT_TILES_DIR)
    parser.add_argument("--repo-id", default="Chrisyichuan/screenshot-training")
    parser.add_argument("--repo-type", default="dataset")
    return parser.parse_args()
