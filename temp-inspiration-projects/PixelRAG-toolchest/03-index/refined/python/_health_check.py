def _health_check(self, port: int) -> bool:
        """Quick HTTP check to see if kiwix-serve is responding."""
        import urllib.request

        try:
            req = urllib.request.Request(f"http://localhost:{port}/", method="HEAD")
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False
