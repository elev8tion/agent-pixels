def prepare(self, n_articles: int = 200, seed: int = 42) -> list[dict]:
        if self._articles is None:
            self._articles = prepare_articles(
                self.zim_path, n_articles, seed, kiwix_url=self.kiwix_url
            )
        return self._articles
