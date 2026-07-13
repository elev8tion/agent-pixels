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
