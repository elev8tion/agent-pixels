def _find_binary(self) -> str:
        for p in self._SEARCH_PATHS:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p
        found = shutil.which("kiwix-serve")
        if found:
            return found
        return self._install_kiwix_tools()
