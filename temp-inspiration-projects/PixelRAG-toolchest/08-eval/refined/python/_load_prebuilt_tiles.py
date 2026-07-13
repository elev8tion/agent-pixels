def _load_prebuilt_tiles(self) -> list[str]:
        """Load ALL .png tiles from a prebuilt tile directory (e.g. hard mini-datastore).

        Unlike _prepare_local_wiki_tiles which only loads golden tiles matching
        example IDs, this loads every tile in the directory — including distractors.
        """
        import glob as _glob

        all_tiles = sorted(_glob.glob(os.path.join(self.prebuilt_tiles_dir, "*.png")))
        filtered = _filter_tiles_by_aspect_ratio(all_tiles)
        logger.info(
            f"prebuilt-tiles: loaded {len(filtered)} tiles from {self.prebuilt_tiles_dir} "
            f"(filtered {len(all_tiles) - len(filtered)} extreme aspect ratio tiles)"
        )
        return filtered
