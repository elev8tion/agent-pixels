def _extract_urls_from_results(self, results: list) -> str:
        """Extract source URLs from tile paths in results, preserving retrieval order."""
        urls = []
        seen = set()
        for item in results:
            # item is (path, score) tuple
            path = item[0] if isinstance(item, tuple) else item
            # Extract example_id from tile path: {example_id}_fullhd_tile_{x}_{y}.png
            filename = os.path.basename(path)
            if "_tile_" in filename:
                example_id = filename.split("_tile_")[0]
                if example_id.endswith("_fullhd"):
                    example_id = example_id[:-7]
                if example_id in self.id_to_url:
                    url = self.id_to_url[example_id]
                    if url not in seen:
                        seen.add(url)
                        urls.append(url)
        return ", ".join(urls)
