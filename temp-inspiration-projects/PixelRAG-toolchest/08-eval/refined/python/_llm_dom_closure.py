async def _llm_dom_closure(self, raw_html: str, chunk_text: str) -> str | None:
        """Use an LLM to find the minimal DOM closure containing the chunk text.

        Sends the article HTML (truncated) and the chunk text to the model,
        asks it to return the minimal enclosing HTML subtree.
        """
        import openai

        # Truncate HTML to avoid context limits — keep first 60K chars
        # (most Wikipedia articles are under 100K)
        html_truncated = raw_html[:60000]

        prompt = f"""Given this HTML document and a text chunk extracted from it, find the minimal DOM subtree that contains ALL the text in the chunk. Return ONLY the raw HTML of that subtree, no explanation.

The text chunk (extracted by Trafilatura, so formatting differs from HTML):
---
{chunk_text[:2000]}
---

The HTML document:
---
{html_truncated}
---

Return the minimal HTML subtree containing all the information from the text chunk. Include complete table/list structures if the chunk spans table cells. Return ONLY HTML, no markdown fences."""

        try:
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model=self.llm_verify_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8000,
                temperature=0,
            )
            result = response.choices[0].message.content.strip()
            # Strip markdown fences if present
            if result.startswith("```"):
                lines = result.split("\n")
                result = "\n".join(
                    lines[1:-1] if lines[-1].startswith("```") else lines[1:]
                )
            return result if "<" in result else None
        except Exception as e:
            logger.warning(f"LLM DOM closure failed: {e}")
            return None
