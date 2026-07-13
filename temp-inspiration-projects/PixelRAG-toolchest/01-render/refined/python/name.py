@property
    def name(self) -> str:
        l = "pw" if self.launcher == "playwright" else "ws"
        surface = "" if self.from_surface else " !surface"
        hs = " HS" if self.headless_shell else ""
        tag = f" [{self.label}]" if self.label else ""
        return f"{self.n_workers}w {self.fmt} {l}{hs}{surface}{tag}"
