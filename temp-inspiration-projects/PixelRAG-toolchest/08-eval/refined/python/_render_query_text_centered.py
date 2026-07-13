def _render_query_text_centered(
        self, text: str, width: int | None = None
    ) -> Image.Image:
        """Render query text centered, reusing wrap logic from PixelQueryRenderer."""
        width = width or self.card_width
        max_text_width = width - 2 * self.padding_x

        # Calculate dynamic font size based on width
        # Ratio: width / 30 seems reasonable (600px -> 20px, 1500px -> 50px)
        dynamic_font_size = max(22, int(width / 30))

        # Use dynamic font if size is different from default
        if dynamic_font_size != self.font_size:
            try:
                font = ImageFont.truetype(self.font_path, dynamic_font_size)
            except Exception:
                font = self.font  # Fallback
        else:
            font = self.font

        lines = _wrap_text_by_pixel_width(text, font, max_text_width)

        line_height = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
        # Scale spacing proportionally
        spacing = max(4, int(self.line_spacing * (dynamic_font_size / self.font_size)))

        total_text_height = len(lines) * line_height + (len(lines) - 1) * spacing
        # Scale padding proportionally
        padding_y = max(
            self.padding_y, int(self.padding_y * (dynamic_font_size / self.font_size))
        )
        text_height = total_text_height + 2 * padding_y

        img = Image.new("RGB", (width, text_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        y = padding_y
        for line in lines:
            bbox = font.getbbox(line)
            line_w = bbox[2] - bbox[0]
            x = (width - line_w) // 2
            draw.text((x, y), line, font=font, fill=(50, 50, 50))
            y += line_height + spacing

        return img
