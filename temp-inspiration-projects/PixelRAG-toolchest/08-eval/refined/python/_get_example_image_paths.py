def _get_example_image_paths(self) -> list[str]:
        """Get image paths for the specific examples."""
        image_paths = []
        for ex in self.examples:
            example_id = ex.get("id", "")
            if not example_id:
                continue
            path = os.path.join(self.screenshot_dir, f"{example_id}_fullhd.png")
            if os.path.exists(path) and os.path.getsize(path) > 0:
                image_paths.append(path)
        return image_paths
