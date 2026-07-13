def _install_kiwix_tools(self) -> str:
        """Auto-download kiwix-tools binary."""
        import platform
        import tarfile
        import tempfile
        import urllib.request

        arch = (
            "x86_64"
            if platform.machine() in ("x86_64", "AMD64")
            else platform.machine()
        )
        url = (
            f"https://download.kiwix.org/release/kiwix-tools/"
            f"kiwix-tools_linux-{arch}-{self._KIWIX_TOOLS_VERSION}.tar.gz"
        )

        install_dir = Path(self._SEARCH_PATHS[0]).parent
        install_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Downloading kiwix-tools %s...", self._KIWIX_TOOLS_VERSION)
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            urllib.request.urlretrieve(url, tmp.name)
            with tarfile.open(tmp.name) as tar:
                for member in tar.getmembers():
                    if member.name.endswith("kiwix-serve"):
                        member.name = "kiwix-serve"
                        tar.extract(member, install_dir)
                    elif member.name.endswith("kiwix-manage"):
                        member.name = "kiwix-manage"
                        tar.extract(member, install_dir)
            os.unlink(tmp.name)

        binary = str(install_dir / "kiwix-serve")
        os.chmod(binary, 0o755)
        logger.info("Installed kiwix-serve to %s", binary)
        return binary
