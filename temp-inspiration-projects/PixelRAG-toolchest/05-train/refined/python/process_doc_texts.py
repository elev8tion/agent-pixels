def process_doc_texts(processor, texts):
    """Wrap document texts in chat template with representation instruction."""
    wrapped = [_DOC_TEXT_PREFIX + t + _DOC_TEXT_SUFFIX for t in texts]
    return processor(text=wrapped, return_tensors="pt", padding="longest")
