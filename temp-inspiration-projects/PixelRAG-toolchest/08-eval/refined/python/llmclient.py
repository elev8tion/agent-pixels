class LLMClient:
    """Simplified async LLM client for Gemini using Vertex AI."""

    def __init__(
        self,
        model: str,
        api_base: str = "http://localhost:8000/v1",
        api_key: str = "dummy",
        temperature: float = 0.0,
        max_tokens: int = 16384,
        timeout: float = 120.0,
        max_context_tokens: int | None = None,
        enable_thinking: bool | None = None,
        force_openai_compat: bool = False,
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_context_tokens = max_context_tokens
        self.enable_thinking = enable_thinking
        print(f"context length model: {max_context_tokens}")

        # Gemini routes to Google GenAI SDK unless forced to OpenAI-compatible
        # (aggregators like OpenRouter / Commonstack expose Gemini via OAI-compat).
        self.is_gemini = ("gemini" in model.lower()) and not force_openai_compat

        if self.is_gemini:
            if not GEMINI_AVAILABLE:
                raise ImportError(
                    "google-genai package is required for Gemini models. Install with: pip install google-genai"
                )

            # Use Vertex AI if GEMINI_API_KEY is set and GOOGLE_GENAI_USE_VERTEXAI is true
            vertex_api_key = os.getenv("GEMINI_API_KEY")
            use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"
            if vertex_api_key and use_vertex:
                logger.info(f"Using Vertex AI for Gemini model: {model}")
                # Ensure GOOGLE_API_KEY is not set when using Vertex AI (it causes conflicts)
                if "GOOGLE_API_KEY" in os.environ:
                    logger.warning(
                        "GOOGLE_API_KEY is set but using Vertex AI. Unsetting GOOGLE_API_KEY to avoid conflicts."
                    )
                    del os.environ["GOOGLE_API_KEY"]
                os.environ["GEMINI_API_KEY"] = vertex_api_key
                os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
                self.gemini_client = genai.Client(
                    http_options=HttpOptions(api_version="v1")
                )
            else:
                # Use standard Gemini API
                logger.info(f"Using standard Gemini API for model: {model}")
                api_key = api_key if api_key != "dummy" else os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError(
                        "GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required for Gemini models"
                    )
                self.gemini_client = genai.Client(api_key=api_key)
        else:
            # Use OpenAI-compatible API
            from openai import AsyncOpenAI

            logger.info(f"Using OpenAI-compatible API: {api_base}")
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=api_base,
                timeout=timeout,
                max_retries=0,
            )
            self.gemini_client = None

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

    async def _generate_gemini(self, messages: list[dict]) -> tuple[str, dict]:
        """Generate using Gemini API."""
        # Extract system prompt and user content
        system_prompt = None
        user_content = None

        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
            elif msg.get("role") == "user":
                user_content = msg.get("content", "")

        # Build parts for Gemini
        parts = []

        # Add system prompt to the beginning of user message if present
        if system_prompt:
            parts.append(Part(text=f"{system_prompt}\n\n"))

        # Process user content
        if isinstance(user_content, str):
            # Simple text
            if parts:
                parts[0] = Part(text=parts[0].text + user_content)
            else:
                parts.append(Part(text=user_content))
        elif isinstance(user_content, list):
            # Multi-modal content
            for item in user_content:
                if item.get("type") == "text":
                    text = item.get("text", "")
                    if (
                        parts
                        and isinstance(parts[0], Part)
                        and hasattr(parts[0], "text")
                    ):
                        # Append to existing text part
                        parts[0] = Part(text=parts[0].text + text)
                    else:
                        parts.append(Part(text=text))
                elif item.get("type") == "image_url":
                    # Extract base64 image
                    image_url = item.get("image_url", {}).get("url", "")
                    if image_url.startswith("data:image"):
                        try:
                            header, data = image_url.split(",", 1)
                            mime_type = header.split(";")[0].split(":")[1]
                            image_bytes = base64.b64decode(data)
                            parts.append(
                                Part(
                                    inline_data=Blob(
                                        mime_type=mime_type, data=image_bytes
                                    )
                                )
                            )
                        except Exception as e:
                            logger.error(f"Failed to process image: {e}")
                            raise

        # Create content
        content = Content(role="user", parts=parts)

        # Call API in executor to avoid blocking
        loop = asyncio.get_event_loop()

        def _call_api():
            try:
                response = self.gemini_client.models.generate_content(
                    model=self.model,
                    contents=[content],
                    config=GenerateContentConfig(
                        temperature=self.temperature, max_output_tokens=self.max_tokens
                    ),
                )
                return response
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                raise

        response = await loop.run_in_executor(None, _call_api)

        # Extract text
        text = response.text if hasattr(response, "text") and response.text else ""

        # Extract usage
        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage_meta = response.usage_metadata
            usage = {
                "prompt_tokens": getattr(usage_meta, "prompt_token_count", 0),
                "completion_tokens": getattr(usage_meta, "candidates_token_count", 0),
                "total_tokens": getattr(usage_meta, "total_token_count", 0),
            }

        return text, usage

    async def _generate_openai(self, messages: list[dict]) -> tuple[str, dict]:
        """Generate using OpenAI-compatible API."""
        kwargs = dict(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )
        # Some modern reasoning models deprecate `temperature` (Claude Opus 4.7+, some GPT-5 variants).
        # Only send it when we actually want to override the default.
        model_lower = self.model.lower()
        drops_temperature = any(
            x in model_lower for x in ("opus-4-7", "opus-4-8", "gpt-5.4-pro")
        )
        if not drops_temperature:
            kwargs["temperature"] = self.temperature
        if self.enable_thinking is not None:
            kwargs["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": self.enable_thinking}
            }
        response = await self.client.chat.completions.create(**kwargs)

        generated_text = response.choices[0].message.content

        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return generated_text, usage

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
