def build_prompt(fewshot_block: str, passage: str, focus_paragraph: str) -> str:
    return f"""You are generating a query-evidence pair for training a text retrieval model over Wikipedia passages.

TASK: Given this passage, generate ONE factual question whose answer is explicitly and completely supported by this passage.

STYLE:
- Write natural search-style questions like SimpleQA, not templates.
- Prefer realistic factual questions a user would actually type into a search engine.
- Use diverse question families such as "what is", "who was", "how many", "in which year", "what did", and similar natural forms.
- Prefer facts stated in a long natural prose paragraph, not list items or table cells.

HARD RULES:
1. SELF-CONTAINED: The question must make sense on its own. Name the relevant entities explicitly.
2. EVIDENCE COMPLETE: The answer must be fully supported by the passage alone.
3. DISTINCTIVE: Include enough detail to identify the fact cleanly.
4. VERBATIM SPAN: `S:` must be copied directly from the passage.
5. PROSE-FIRST: Use the long prose paragraph below as the evidence anchor. If it does not support a good question, write `SKIP`.

SKIP if any is true:
- The passage is mostly raw list junk, track listings, or vote counts.
- The long prose paragraph below does not support a clean question-answer pair.
- You cannot write a self-contained question.
- The answer is not fully supported by this passage.
- The supporting span would be truncated or fragmentary.

Write exactly `SKIP` if the passage should be skipped.

source_type: prose | infobox | table | list | other

Few-shot examples:

{fewshot_block}

Now generate for this new passage.

Preferred long prose paragraph:
\"\"\"
{focus_paragraph}
\"\"\"

Passage:
\"\"\"
{passage}
\"\"\"

Output format (4 lines only):
Q: <natural self-contained question>
A: <concise answer>
S: <verbatim supporting span from the passage>
T: <source_type>"""
