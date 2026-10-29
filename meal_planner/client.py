"""Small OpenAI-compatible chat client using only the standard library."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class MealPlannerClient:
    """Posts chat/completions to an OpenAI-compatible endpoint (default Ollama)."""

    def __init__(
        self,
        endpoint: str,
        model: str,
        api_key: str | None = None,
        timeout: int = 60,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.7) -> dict[str, Any]:
        """Send a chat request and return the parsed JSON response."""
        url = f"{self.endpoint}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Endpoint returned HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not reach endpoint {self.endpoint}: {exc}"
            ) from exc
        return json.loads(raw)

    def chat_content(self, messages: list[dict[str, str]], temperature: float = 0.7) -> str:
        """Send a chat request and return the assistant message content string."""
        response = self.chat(messages, temperature=temperature)
        choices = response.get("choices") or []
        if not choices:
            raise RuntimeError("Endpoint returned no choices")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if content is None:
            raise RuntimeError("Endpoint returned no message content")
        return str(content)
