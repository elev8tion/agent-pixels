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
