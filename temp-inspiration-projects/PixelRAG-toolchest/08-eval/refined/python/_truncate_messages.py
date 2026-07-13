def _truncate_messages(self, messages: list[dict], max_tokens: int) -> list[dict]:
        """Truncate text content in messages to fit within token limit."""
        # Reserve tokens for response
        available_tokens = max_tokens - self.max_tokens - 500  # buffer
        max_chars = available_tokens * 4

        truncated = []
        total_chars = 0

        for msg in messages:
            new_msg = msg.copy()
            content = msg.get("content", "")

            if isinstance(content, str):
                if total_chars + len(content) > max_chars:
                    remaining = max(0, max_chars - total_chars)
                    new_msg["content"] = (
                        content[:remaining]
                        + "\n\n[Content truncated due to context limit]"
                    )
                    logger.warning(
                        f"Truncated message content from {len(content)} to {remaining} chars"
                    )
                total_chars += len(new_msg["content"])
            elif isinstance(content, list):
                new_content = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        if total_chars + len(text) > max_chars:
                            remaining = max(0, max_chars - total_chars)
                            new_item = item.copy()
                            new_item["text"] = (
                                text[:remaining]
                                + "\n\n[Content truncated due to context limit]"
                            )
                            new_content.append(new_item)
                            logger.warning(
                                f"Truncated text content from {len(text)} to {remaining} chars"
                            )
                            total_chars += remaining
                        else:
                            new_content.append(item)
                            total_chars += len(text)
                    else:
                        new_content.append(item)
                        if isinstance(item, dict) and item.get("type") == "image_url":
                            total_chars += 1000 * 4  # image token estimate
                new_msg["content"] = new_content
            truncated.append(new_msg)

        return truncated
