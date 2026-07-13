def _render_image(self, text: str) -> Image.Image:
        """Render *text* to a PIL Image (white bg, black text)."""
        max_text_width = self.img_width - 2 * self.padding_x
        lines = _wrap_text_by_pixel_width(text, self.font, max_text_width)

        # Measure line height using a reference string
        line_height = self.font.getbbox("Ay")[3] - self.font.getbbox("Ay")[1]
        total_text_height = (
            len(lines) * line_height + (len(lines) - 1) * self.line_spacing
        )
        img_height = total_text_height + 2 * self.padding_y

        img = Image.new("RGB", (self.img_width, img_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        y = self.padding_y
        for line in lines:
            draw.text((self.padding_x, y), line, font=self.font, fill=(0, 0, 0))
            y += line_height + self.line_spacing

        return img
