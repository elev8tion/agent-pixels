def forward_query(model, inputs, bidirectional=False):
    """Forward text query through model → normalized embedding."""
    _clear_rope_deltas(model)
    return model(**inputs, bidirectional=bidirectional)
