def _load_redirect_set(self) -> set[int]:
        if self._redirect_ids is not None:
            return self._redirect_ids
        redirects = self._build_redirect_map()
        self._redirect_ids = {int(k) for k in redirects}
        return self._redirect_ids
