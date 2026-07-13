def make_source(config):
    source_config = dict(config.get("source", {}))
    source_type = source_config.pop("type", "local")
    # Expand ~ in any string values that look like paths
    for k, v in source_config.items():
        if isinstance(v, str) and ("/" in v or "~" in v):
            source_config[k] = str(Path(v).expanduser())
    return SOURCES[source_type](**source_config)
