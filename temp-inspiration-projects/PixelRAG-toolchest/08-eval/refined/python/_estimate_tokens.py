def _estimate_tokens(self, messages: list[dict]) -> int:
        """Estimate token count from messages (rough: ~4 chars per token)."""
        total_chars = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            total_chars += len(item.get("text", ""))
                        elif item.get("type") == "image_url":
                            # Rough estimate for image tokens
                            total_chars += 1000 * 4  # ~1000 tokens per image
        return total_chars // 4
