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
