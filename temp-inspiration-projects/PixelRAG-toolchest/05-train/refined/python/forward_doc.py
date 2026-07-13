def forward_doc(model, inputs, bidirectional=False):
    """Forward image document through model → normalized embedding."""
    _clear_rope_deltas(model)
    return model(**inputs, bidirectional=bidirectional)
