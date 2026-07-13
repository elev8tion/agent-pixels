def set_instruction(instruction: str) -> None:
    """Set the embedding instruction for all backends."""
    global _INSTRUCTION
    _INSTRUCTION = instruction
    logger.info("Embedding instruction set to: %r", instruction)
