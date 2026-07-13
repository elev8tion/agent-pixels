@staticmethod
    def _extract_search_keys(chunk_text: str) -> list[str]:
        """Extract distinctive search keys from chunk text for DOM matching.

        Detects chunk type (table-heavy vs prose-heavy) and picks the best strategy.
        Returns keys ordered by distinctiveness — first key is tried first in DOM lookup.
        """
        import re

        lines = chunk_text.split("\n")
        # Skip first line if it looks like an article title (short, no pipes, no punctuation)
        # These match <h1> in DOM and cause Bug 1
        if lines and len(lines[0]) < 80 and "|" not in lines[0] and "." not in lines[0]:
            content_lines = lines[1:]
        else:
            content_lines = lines
        table_lines = [l for l in content_lines if "|" in l and "---" not in l]
        prose_lines = [
            l
            for l in content_lines
            if len(l) > 30 and "|" not in l and not l.startswith("- ^")
        ]
        is_table_heavy = (
            len(table_lines) > len(content_lines) * 0.4 if content_lines else False
        )

        keys = []

        if is_table_heavy:
            # Mixed strategy: include keys from BOTH table cells and prose
            # so coverage scorer can find a container spanning both parts.
            cell_candidates = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.split("|") if c.strip()]
                for cell in cells:
                    if len(cell) < 5 or len(cell) > 80:
                        continue
                    if cell.lower() in ("yes", "no", "n/a", "none", ""):
                        continue
                    has_code = bool(re.search(r"[A-Z]\d|[a-z]\d{4,}", cell))
                    has_mixed = bool(re.search(r"\d.*[a-zA-Z]|[a-zA-Z].*\d", cell))
                    has_proper = bool(re.search(r"[A-Z][a-z]+\s+[A-Z]", cell))
                    if has_code or has_mixed or has_proper:
                        cell_candidates.insert(0, cell)
                    elif len(cell) > 12:
                        cell_candidates.append(cell)

            # Table cells first (these anchor to the infobox)
            for cc in cell_candidates[:3]:
                if cc not in keys:
                    keys.append(cc)

            # Then prose keys (these anchor to body paragraphs)
            for line in prose_lines[:3]:
                mid = len(line) // 2
                candidate = line[mid - 15 : mid + 15].strip()
                if len(candidate) >= 10 and re.search(r"[a-zA-Z]{4,}", candidate):
                    keys.append(candidate)

        else:
            # Prose-dominant chunk: use prose fragments as primary keys
            for line in prose_lines[:4]:
                mid = len(line) // 2
                candidate = line[mid - 15 : mid + 15].strip()
                if len(candidate) >= 10 and re.search(r"[a-zA-Z]{4,}", candidate):
                    keys.append(candidate)

            # Add table cell values as secondary
            if table_lines:
                for tl in table_lines[:5]:
                    cells = [
                        c.strip()
                        for c in tl.split("|")
                        if c.strip() and len(c.strip()) > 8
                    ]
                    for cell in cells[:1]:
                        if cell not in keys:
                            keys.append(cell)

        # List item content
        if not keys:
            list_lines = [
                l[2:]
                for l in lines
                if l.startswith("- ") and len(l) > 20 and not l.startswith("- ^")
            ]
            for ll in list_lines[:3]:
                mid = len(ll) // 2
                candidate = ll[mid - 15 : mid + 15].strip()
                if len(candidate) >= 10:
                    keys.append(candidate)

        # Fallback
        if not keys and len(chunk_text) > 40:
            candidate = chunk_text[10:50].strip()
            keys.append(candidate)

        return keys
