def create_sample_html(output_dir: Path) -> list[Path]:
    """Create sample HTML files to demonstrate local file ingestion."""
    html_dir = output_dir / "sample_html"
    html_dir.mkdir(parents=True, exist_ok=True)

    files = []

    # A simple article-style page
    p1 = html_dir / "visual_retrieval.html"
    p1.write_text(
        SAMPLE_HTML.format(
            title="Visual Document Retrieval",
            body=(
                "Visual document retrieval captures documents as images and uses "
                "vision-language models to embed them into a shared vector space. "
                "Unlike text-based retrieval which requires parsing, visual retrieval "
                "preserves <span class='highlight'>layout, tables, figures, and formatting</span> "
                "that text extraction often loses."
            ),
            extra="""
<h2>Comparison</h2>
<table>
<tr><th>Method</th><th>Preserves Layout</th><th>Handles Tables</th><th>Needs Parser</th></tr>
<tr><td>Text extraction</td><td>No</td><td>Partial</td><td>Yes</td></tr>
<tr><td>HTML rendering</td><td>Partial</td><td>Yes</td><td>Yes</td></tr>
<tr><td><b>Visual (screenshot)</b></td><td><b>Yes</b></td><td><b>Yes</b></td><td><b>No</b></td></tr>
</table>
""",
        )
    )
    files.append(p1)

    # A data-heavy page with tables
    p2 = html_dir / "benchmark_results.html"
    rows = "".join(
        f"<tr><td>Config {i}</td><td>{70 + i * 1.3:.1f}</td><td>{0.5 + i * 0.02:.2f}s</td><td>{'LoRA' if i % 2 else 'Base'}</td></tr>"
        for i in range(15)
    )
    p2.write_text(
        SAMPLE_HTML.format(
            title="PixelRAG Benchmark Results",
            body="Evaluation results across different configurations and model variants.",
            extra=f"""
<h2>SimpleQA Retrieval Scores</h2>
<table>
<tr><th>Configuration</th><th>Recall@1</th><th>Latency</th><th>Model</th></tr>
{rows}
</table>
""",
        )
    )
    files.append(p2)

    return files
