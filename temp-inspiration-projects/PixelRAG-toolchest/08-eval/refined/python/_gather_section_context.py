def _gather_section_context(self, elem) -> "lxml_html.HtmlElement":  # noqa: F821
        """Gather all sibling elements within the same h2/h3 section."""
        from lxml import etree

        # Walk up to find direct child of mw-parser-output
        current = elem
        mw_output = None
        while current is not None:
            parent = current.getparent()
            if parent is not None:
                classes = parent.get("class", "")
                if "mw-parser-output" in classes:
                    mw_output = parent
                    break
            current = parent

        if mw_output is None:
            return elem

        # Find the element's position among mw-parser-output children
        children = list(mw_output)
        try:
            idx = children.index(current)
        except ValueError:
            return elem

        # Gather backward until we hit a heading, forward until next heading
        section_elems = [current]

        # Backward
        for i in range(idx - 1, max(idx - 10, -1), -1):
            child = children[i]
            if hasattr(child, "tag") and child.tag in ("h1", "h2", "h3"):
                section_elems.insert(0, child)
                break
            section_elems.insert(0, child)

        # Forward
        for i in range(idx + 1, min(idx + 10, len(children))):
            child = children[i]
            if hasattr(child, "tag") and child.tag in ("h1", "h2", "h3"):
                break
            section_elems.append(child)

        # Build a container div with these elements
        container = etree.Element("div")
        for el in section_elems:
            try:
                container.append(el)
            except Exception:
                pass

        return container
