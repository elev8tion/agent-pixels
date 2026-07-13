def _get_zim(self):
        if self._zim is None:
            from libzim.reader import Archive

            self._zim = Archive(str(self.zim_path))
        return self._zim
