async def generate(
        self, messages: list[dict], max_retries: int = 3, connection_retries: int = 12
    ) -> tuple[str, dict]:
        """Generate response from messages with retry on timeout/connection errors.

        Args:
            max_retries: Retry count for timeout errors.
            connection_retries: Retry count for connection errors (server restart).
                12 retries × 10s = ~2 min window for server to come back.

        Returns:
            Tuple of (generated_text, usage_dict).
        """
        # Check and truncate if needed
        if hasattr(self, "max_context_tokens") and self.max_context_tokens:
            estimated_tokens = self._estimate_tokens(messages)
            if estimated_tokens > self.max_context_tokens - self.max_tokens:
                logger.warning(
                    f"Estimated {estimated_tokens} tokens exceeds limit, truncating..."
                )
                messages = self._truncate_messages(messages, self.max_context_tokens)

        conn_attempts = 0
        timeout_attempts = 0
        while True:
            try:
                if self.is_gemini:
                    return await self._generate_gemini(messages)
                else:
                    return await self._generate_openai(messages)
            except asyncio.TimeoutError:
                timeout_attempts += 1
                if timeout_attempts >= max_retries:
                    raise
                wait_time = 2**timeout_attempts  # 2, 4, 8 seconds
                logger.warning(
                    f"Timeout on attempt {timeout_attempts}/{max_retries}, retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)
            except Exception as e:
                error_str = str(e).lower()
                if "timeout" in error_str or "timed out" in error_str:
                    timeout_attempts += 1
                    if timeout_attempts >= max_retries:
                        raise
                    wait_time = 2**timeout_attempts
                    logger.warning(
                        f"Timeout on attempt {timeout_attempts}/{max_retries}, retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                elif "connection" in error_str or "connect" in error_str:
                    conn_attempts += 1
                    if conn_attempts >= connection_retries:
                        raise
                    wait_time = 10  # fixed 10s — server restart takes ~30-60s
                    logger.warning(
                        f"Connection error ({conn_attempts}/{connection_retries}), retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                elif (
                    "429" in error_str
                    or "rate_limit" in error_str
                    or "rate limit" in error_str
                ):
                    # Provider rate limit — exponential backoff with jitter
                    timeout_attempts += 1
                    if timeout_attempts >= max_retries + 3:  # extra patience for 429
                        raise
                    import random

                    wait_time = min(60, 5 * (2**timeout_attempts)) + random.uniform(
                        0, 3
                    )
                    logger.warning(
                        f"429 rate-limit (attempt {timeout_attempts}), backing off {wait_time:.1f}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise
