def render(
        self,
        example_id: str,
        query_text: str,
        query_image_path: str | None,
        force: bool = False,
    ) -> str:
        """Render query image + text into one card, save to disk.

        Layout: image on top, text below (same for iNaturalist and Landmarks).

        Args:
            example_id: Example identifier for filename.
            query_text: The question text to render below the image.
            query_image_path: Path to the query image (iNaturalist or Landmark photo).
                If None or file missing, only the text is rendered.
            force: If True, re-render even if output exists (e.g. when images were added later).

        Returns:
            Path to the saved PNG.
        """
        out_path = os.path.join(self.output_dir, f"{example_id}_query_card.png")
        if os.path.exists(out_path) and not force:
            return out_path

        # Load query image
        if query_image_path and os.path.exists(query_image_path):
            try:
                query_img = Image.open(query_image_path).convert("RGB")
                # Resize if too large to ensure font size is readable and image isn't massive
                max_dim = 1536  # Standard reasonable max dimension
                if max(query_img.size) > max_dim:
                    ratio = max_dim / max(query_img.size)
                    new_size = (
                        int(query_img.width * ratio),
                        int(query_img.height * ratio),
                    )
                    query_img = query_img.resize(new_size, Image.Resampling.LANCZOS)
            except Exception as e:
                logger.warning(f"Failed to load query image {query_image_path}: {e}")
                query_img = None
        else:
            query_img = None

        # Card width adapts to image: expand if image is wider than card_width
        if query_img is not None:
            effective_width = max(
                self.card_width, query_img.width + 2 * self.image_padding
            )
        else:
            effective_width = self.card_width

        # Render query text at effective width
        text_img = self._render_query_text_centered(query_text, effective_width)

        # Compose: image on top, text below with padding for balanced look
        if query_img is not None:
            img_section_height = query_img.height + 2 * self.image_padding
        else:
            img_section_height = 0

        text_section_height = text_img.height + 2 * self.text_section_padding
        total_height = img_section_height + text_section_height

        card = Image.new("RGB", (effective_width, total_height), color=(255, 255, 255))
        ImageDraw.Draw(card)

        y_offset = 0
        if query_img is not None:
            x_center = (effective_width - query_img.width) // 2
            card.paste(query_img, (x_center, self.image_padding))
            y_offset = img_section_height

        # Center text block in its section
        text_y = y_offset + self.text_section_padding
        card.paste(text_img, (0, text_y))

        # Optional: rounded corners (simplified - draw white rounded rect overlay)
        if self.border_radius > 0:
            # Create mask for rounded corners
            mask = Image.new("L", card.size, 255)
            m_draw = ImageDraw.Draw(mask)
            m_draw.rounded_rectangle(
                (0, 0, card.width - 1, card.height - 1),
                radius=self.border_radius,
                fill=255,
                outline=0,
            )
            # For simple output we keep the card as-is; full rounded crop would need alpha
            pass

        card.save(out_path)
        logger.debug(f"Rendered query card: {out_path} ({card.size[0]}x{card.size[1]})")
        return out_path
