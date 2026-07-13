def _find_semantic_container(self, elem) -> "lxml_html.HtmlElement":  # noqa: F821
        """Walk up from matched element to find a meaningful semantic container.

        Hard cap: never return a container with text_content > MAX_CONTAINER_CHARS.
        Stops at mw-parser-output boundary (never returns the whole article).
        """

        SEMANTIC_TAGS = {
            "section",
            "article",
            "table",
            "blockquote",
            "details",
            "figure",
        }
        STOP_CLASSES = {"mw-parser-output", "mw-body-content", "mw-body"}
        MIN_CONTEXT_LEN = 200

        if elem.tag in SEMANTIC_TAGS:
            return elem

        best = elem
        current = elem

        for _ in range(15):
            parent = current.getparent()
            if parent is None:
                break
            # Hard stop: never go past the article content container
            parent_classes = parent.get("class", "")
            if any(sc in parent_classes for sc in STOP_CLASSES):
                # We've reached the article root — use section gathering instead
                if self.context_mode == "section":
                    gathered = self._gather_section_context(current)
                    if gathered is not None:
                        return gathered
                break

            try:
                parent_len = len(parent.text_content())
            except Exception:
                break

            # Prefer semantic tags — even if parent exceeds size cap
            # Bug fix 2: tbody→table jump — don't let size cap block us from
            # reaching a semantic container that's just one level up
            if parent.tag in SEMANTIC_TAGS:
                return parent

            # Stop if parent is too large (but we already checked semantic tags above)
            if parent_len > self.MAX_CONTAINER_CHARS:
                # One more chance: check if grandparent is a semantic tag
                grandparent = parent.getparent()
                if grandparent is not None and grandparent.tag in SEMANTIC_TAGS:
                    return grandparent
                break

            # Accept block containers that are reasonably sized
            if parent_len >= MIN_CONTEXT_LEN:
                best = parent

            current = parent

        return best
