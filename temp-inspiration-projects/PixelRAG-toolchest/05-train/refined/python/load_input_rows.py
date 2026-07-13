def load_input_rows(args: argparse.Namespace) -> list[dict]:
    rows = []
    matched = [Path(path) for path in sorted(glob.glob(args.input_glob))]
    if not matched:
        raise FileNotFoundError(f"No files matched --input-glob={args.input_glob}")

    row_id = 0
    for path in matched:
        for line_no, payload in iter_rows(path):
            query = payload.get("query") or payload.get("question")
            if not isinstance(query, str) or not query.strip():
                continue
            rows.append(
                {
                    "row_id": row_id,
                    "source_file": str(path),
                    "source_line": line_no,
                    "query": query.strip(),
                    "payload": payload,
                }
            )
            row_id += 1
            if args.limit > 0 and len(rows) >= args.limit:
                return rows
    return rows
