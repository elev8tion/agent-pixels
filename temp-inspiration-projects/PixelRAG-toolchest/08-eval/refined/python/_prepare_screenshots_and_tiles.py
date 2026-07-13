def _prepare_screenshots_and_tiles(self) -> list[str]:
        """Prepare screenshots and tiles for dataset, return tile paths.

        Uses deduplicated examples (one per unique URL) to avoid
        duplicate tiles inflating the retrieval index.
        """
        from .simpleqa_data import capture_screenshot_for_example, split_image_to_tiles
        from tqdm import tqdm

        examples_to_process = self._dedup_examples
        screenshot_paths = []
        missing = []

        # Collect screenshot paths and identify missing (deduplicated)
        for ex in examples_to_process:
            screenshot_path = os.path.join(
                self.screenshot_dir, f"{ex['id']}_fullhd.png"
            )
            screenshot_paths.append(screenshot_path)
            if (
                not os.path.exists(screenshot_path)
                or os.path.getsize(screenshot_path) == 0
            ):
                missing.append(ex)

        # Capture missing screenshots
        if missing:
            logger.info(f"Preparing {len(missing)} missing screenshots...")
            for ex in tqdm(missing, desc="Capturing screenshots"):
                capture_screenshot_for_example(ex, self.screenshot_dir)
            logger.info("Screenshots prepared.")

        # Split each screenshot into tiles
        all_tile_paths = []
        logger.info(
            f"Splitting {len(screenshot_paths)} unique screenshots into tiles (output: {self.tiles_dir})..."
        )
        for screenshot_path in tqdm(screenshot_paths, desc="Splitting tiles"):
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                tile_paths = split_image_to_tiles(
                    screenshot_path, self.tiles_dir, self.tile_size, self.overlap
                )
                all_tile_paths.extend(tile_paths)

        # Filter out tiles with extreme aspect ratios
        filtered_tile_paths = _filter_tiles_by_aspect_ratio(all_tile_paths)
        logger.info(
            f"Prepared {len(filtered_tile_paths)} tiles from {len(screenshot_paths)} unique screenshots "
            f"(filtered {len(all_tile_paths) - len(filtered_tile_paths)} extreme aspect ratio tiles)"
        )
        return filtered_tile_paths
