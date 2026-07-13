def load_nq_tables_data(num_examples: int | None = 1000) -> list[dict]:
    """Load NQ-Tables dev split (table subset of Natural Questions).

    NQ-Tables filters Natural Questions to only keep examples where the gold
    answer resides inside a Wikipedia HTML table. Each example includes the
    full table content (columns + rows) and the Wikipedia URL.

    Source: GCS gs://tapas_models/2021_07_22/nq_tables/interactions/dev.jsonl
    Reference: Herzig et al. (2021), "Open Domain Question Answering over
    Tables via Dense Retrieval" (NAACL 2021).

    Args:
        num_examples: Number of examples to return. Default 1000.

    Returns:
        List of dicts with id, problem, gold_answers, metadata.
    """
    import html as _html

    data_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "nq_tables", "dev.jsonl"
    )
    data_path = os.path.abspath(data_path)

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"NQ-Tables data not found at {data_path}. "
            "Download with: gsutil cp gs://tapas_models/2021_07_22/nq_tables/interactions/dev.jsonl data/nq_tables/"
        )

    logger.info(f"Loading NQ-Tables dev split from {data_path}...")

    import json as _json

    data = []
    with open(data_path) as f:
        for line in f:
            ex = _json.loads(line)
            questions = ex.get("questions", [])
            if not questions:
                continue

            q = questions[0]
            question_text = q.get("originalText", "")
            answer_texts = q.get("answer", {}).get("answerTexts", [])

            if not question_text or not answer_texts:
                continue

            gold_answers = [a.strip() for a in answer_texts if a.strip()]
            if not gold_answers:
                continue

            # Extract Wikipedia URL from table metadata
            table = ex.get("table", {})
            doc_url = table.get("documentUrl", "")
            doc_url = _html.unescape(doc_url)
            # Normalize NQ URL format: /w/index.php?title=Foo&oldid=123 -> /wiki/Foo
            _title_match = re.search(r"[?&]title=([^&]+)", doc_url)
            if _title_match:
                doc_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(_title_match.group(1), safe='/:(),-')}"

            example = {
                "id": ex.get("id", hashlib.md5(question_text.encode()).hexdigest()),
                "problem": question_text,
                "gold_answers": gold_answers,
                "metadata": {
                    "urls": [doc_url] if doc_url else [],
                    "dataset": "nq_tables",
                    "document_title": table.get("documentTitle", ""),
                    "table_id": table.get("tableId", ""),
                },
            }
            data.append(example)

            if num_examples and len(data) >= num_examples:
                break

    logger.info(f"Loaded {len(data)} NQ-Tables examples.")
    return data
