class PixelQueryRenderer:
    """Renders text queries as small, clear PNG images.

    Images are cached on disk so each query is only rendered once.
    """

    def __init__(
        self,
        output_dir: str = "pixel_queries",
        font_path: str | None = None,
        font_size: int = 16,
        img_width: int = 600,
        padding_x: int = 16,
        padding_y: int = 12,
        line_spacing: int = 4,
    ):
        self.output_dir = output_dir
        self.font_path = _find_font(font_path)
        self.font_size = font_size
        self.img_width = img_width
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.line_spacing = line_spacing

        os.makedirs(output_dir, exist_ok=True)
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        logger.info(
            f"PixelQueryRenderer: dir={output_dir}, font={os.path.basename(self.font_path)}, "
            f"size={font_size}, width={img_width}"
        )

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

    def render(self, example_id: str, query_text: str) -> str:
        """Render a query and return the path to the saved PNG.

        If the image already exists on disk it is *not* re-rendered.
        """
        out_path = os.path.join(self.output_dir, f"{example_id}_query.png")
        if os.path.exists(out_path):
            return out_path

        img = self._render_image(query_text)
        img.save(out_path)
        logger.debug(f"Rendered pixel query: {out_path} ({img.size[0]}x{img.size[1]})")
        return out_path

    def render_all(self, examples: list[dict]) -> dict[str, str]:
        """Batch-render pixel queries for a list of examples.

        Args:
            examples: List of dicts with at least ``id`` and ``problem`` keys.

        Returns:
            Dict mapping example_id → pixel query image path.
        """
        id_to_path: dict[str, str] = {}
        rendered, cached = 0, 0
        for ex in examples:
            eid = ex["id"]
            path = os.path.join(self.output_dir, f"{eid}_query.png")
            if os.path.exists(path):
                cached += 1
            else:
                img = self._render_image(ex["problem"])
                img.save(path)
                rendered += 1
            id_to_path[eid] = path

        logger.info(
            f"PixelQueryRenderer: {rendered} rendered, {cached} cached, "
            f"{rendered + cached} total in {self.output_dir}"
        )
        return id_to_path
