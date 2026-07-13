def _parse_infobox(self, wikitext: str) -> str:
        """Parse infobox from wikitext and convert to plain text."""
        import re

        # Find infobox start
        start = wikitext.find("{{Infobox")
        if start == -1:
            start = wikitext.find("{{infobox")
        if start == -1:
            return ""

        # Count braces to find matching end
        depth = 0
        end = start
        for i in range(start, len(wikitext)):
            if wikitext[i : i + 2] == "{{":
                depth += 1
            elif wikitext[i : i + 2] == "}}":
                depth -= 1
                if depth == 0:
                    end = i + 2
                    break

        infobox_raw = wikitext[start:end]

        # Parse fields
        lines = []
        for match in re.finditer(
            r"\|\s*([^=|]+?)\s*=\s*([^|]*?)(?=\n\s*\||\}\})", infobox_raw, re.DOTALL
        ):
            key = match.group(1).strip()
            value = match.group(2).strip()

            # Skip image-related fields
            if key.lower() in (
                "image",
                "caption",
                "alt",
                "width",
                "height",
                "image_size",
                "imagesize",
            ):
                continue

            # Clean up wikitext markup
            value = re.sub(
                r"\{\{[^}|]*\|([^}]*)\}\}", r"\1", value
            )  # {{template|value}} -> value
            value = re.sub(
                r"\[\[([^|\]]*\|)?([^\]]*)\]\]", r"\2", value
            )  # [[link|text]] -> text
            value = re.sub(r"'''?", "", value)  # bold/italic
            value = re.sub(r"<[^>]+>", "", value)  # HTML tags
            value = re.sub(r"\{\{[^}]*\}\}", "", value)  # remaining templates
            value = " ".join(value.split())  # normalize whitespace

            if value:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)
