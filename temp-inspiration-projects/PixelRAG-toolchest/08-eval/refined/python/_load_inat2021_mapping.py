@classmethod
    def _load_inat2021_mapping(cls) -> dict[int, str]:
        """Load iNaturalist 2021 competition image_id -> file_name mapping.

        Downloads val.json from the competition S3 bucket if not cached locally.
        """
        if cls._inat2021_id_map is not None:
            return cls._inat2021_id_map

        import json
        import tarfile
        import urllib.request
        from pathlib import Path

        data_dir = Path(cls.INAT2021_DATA_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        val_json = data_dir / "val.json"

        if not val_json.exists():
            tar_path = data_dir / "val.json.tar.gz"
            if not tar_path.exists():
                logger.info("Downloading iNaturalist 2021 val annotations...")
                urllib.request.urlretrieve(
                    "https://ml-inat-competition-datasets.s3.amazonaws.com/2021/val.json.tar.gz",
                    str(tar_path),
                )
            with tarfile.open(str(tar_path), "r:gz") as tf:
                tf.extractall(path=str(data_dir))
            logger.info(f"Extracted iNat 2021 val.json to {val_json}")

        with open(val_json) as f:
            data = json.load(f)

        cls._inat2021_id_map = {img["id"]: img["file_name"] for img in data["images"]}
        logger.info(f"Loaded iNat 2021 mapping: {len(cls._inat2021_id_map)} images")
        return cls._inat2021_id_map
