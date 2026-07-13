async def _ocr_one(self, path: str, session) -> str:
        if path in self._cache:
            return self._cache[path]
        import aiohttp
        import base64

        try:
            with open(path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("ascii")
        except Exception as e:
            logger.error(f"OCR read failed for {path}: {e}")
            return ""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                        },
                        {"type": "text", "text": self.prompt},
                    ],
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": 0.0,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with session.post(
                f"{self.ocr_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    logger.error(f"OCR HTTP {resp.status} for {path}: {err[:200]}")
                    return ""
                result = await resp.json()
                text = result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OCR request failed for {path}: {e}")
            return ""
        self._append_cache(path, text)
        return text
