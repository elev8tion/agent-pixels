def _prepare_screenshots(self) -> list[str]:
        """Prepare screenshots for dataset and return list of paths."""
        from .simpleqa_data import capture_screenshot_for_example

        screenshot_paths = []
        missing = []

        for ex in self.examples:
            screenshot_path = os.path.join(
                self.screenshot_dir, f"{ex['id']}_fullhd.png"
            )
            screenshot_paths.append(screenshot_path)
            if (
                not os.path.exists(screenshot_path)
                or os.path.getsize(screenshot_path) == 0
            ):
                missing.append(ex)

        if missing:
            logger.info(
                f"Found {len(missing)} missing screenshots out of {len(self.examples)} total examples"
            )
            logger.info(f"Preparing {len(missing)} missing screenshots...")
            # Use a more robust approach: continue even if some screenshots fail
            success_count = 0
            for ex in missing:
                try:
                    capture_screenshot_for_example(ex, self.screenshot_dir)
                    success_count += 1
                except Exception as e:
                    logger.warning(
                        f"Failed to capture screenshot for {ex.get('id', 'unknown')}: {e}"
                    )
                    # Continue with next screenshot instead of failing completely
            logger.info(
                f"Screenshots prepared: {success_count}/{len(missing)} successful"
            )
        else:
            logger.info(
                f"All {len(self.examples)} screenshots already exist, skipping preparation"
            )

        # Return only existing screenshots
        return [
            p for p in screenshot_paths if os.path.exists(p) and os.path.getsize(p) > 0
        ]
