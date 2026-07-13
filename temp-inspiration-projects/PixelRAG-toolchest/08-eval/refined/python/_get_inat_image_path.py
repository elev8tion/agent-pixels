def _get_inat_image_path(self, example: dict) -> str | None:
        """Get EVQA query image (iNaturalist or Landmarks). Delegates to _get_query_image_path_for_example."""
        return _get_query_image_path_for_example(example, self.tiles_dir)
