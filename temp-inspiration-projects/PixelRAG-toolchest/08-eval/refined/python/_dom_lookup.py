def _dom_lookup(self, html: str, chunk_text: str) -> str | None:
        """Find the contiguous DOM span covering chunk_text, return its HTML.

        Strategy:
        1. Extract search keys from chunk text (table cells + prose fragments)
        2. For each key, find the tightest DOM element and walk up to a
           direct child of mw-parser-output
        3. Return ALL direct children from the first match to the last match
           (inclusive), plus everything in between — this preserves the full
           contiguous region the chunk spans.
        """
        from lxml import html as lxml_html, etree

        tree = lxml_html.fromstring(html)

        keys = self._extract_search_keys(chunk_text)
        if not keys:
            return None

        mw_output = tree.xpath('//div[contains(@class, "mw-parser-output")]')
        if not mw_output:
            return None
        content_root = mw_output[0]
        children = list(content_root)
        if not children:
            return None

        # For each key, find the tightest match and resolve to a
        # direct-child index of mw-parser-output
        matched_child_indices = set()
        SKIP_TAGS = frozenset(
            ("script", "style", "title", "meta", "link", "nav", "header", "footer")
        )

        for key in keys:
            key_norm = self._normalize(key)
            if len(key_norm) < 4:
                continue

            best_elem = None
            best_len = float("inf")

            for elem in content_root.iter():
                if not isinstance(elem, lxml_html.HtmlElement):
                    continue
                if elem.tag in SKIP_TAGS:
                    continue
                try:
                    tc = elem.text_content()
                except Exception:
                    continue
                tc_norm = self._normalize(tc)
                if key_norm in tc_norm and len(tc) < best_len:
                    best_elem = elem
                    best_len = len(tc)

            if best_elem is None:
                continue

            # Walk up from best_elem to find which direct child of content_root
            # contains it
            current = best_elem
            while current is not None:
                parent = current.getparent()
                if parent is None:
                    break
                if parent == content_root:
                    # current is a direct child of mw-parser-output
                    try:
                        idx = children.index(current)
                        matched_child_indices.add(idx)
                    except ValueError:
                        pass
                    break
                current = parent

        if not matched_child_indices:
            return None

        # Return contiguous range from first to last matched child (inclusive)
        first = min(matched_child_indices)
        last = max(matched_child_indices)

        span_elems = children[first : last + 1]

        # Build result: serialize all elements in the span
        parts = []
        for el in span_elems:
            # Strip style/script/navbox noise
            for tag in ("style", "script"):
                for junk in list(el.iter(tag)):
                    if junk.getparent() is not None:
                        junk.getparent().remove(junk)
            if hasattr(el, "xpath"):
                for nav in el.xpath('.//*[contains(@class, "navbox")]'):
                    if nav.getparent() is not None:
                        nav.getparent().remove(nav)
            try:
                parts.append(etree.tostring(el, encoding="unicode", method="html"))
            except Exception:
                continue

        if not parts:
            return None

        html_str = "\n".join(parts)

        # Log oversized results but still return them (caller decides)
        if len(html_str) > self.MAX_CONTAINER_CHARS * 2:
            logger.warning(
                "DOM lookup oversized: %d chars (max %d) for chunk starting with %r",
                len(html_str),
                self.MAX_CONTAINER_CHARS * 2,
                chunk_text[:50],
            )

        # Minimum useful size
        if len(html_str) < 100 and len(chunk_text) > 200:
            return None

        return html_str
