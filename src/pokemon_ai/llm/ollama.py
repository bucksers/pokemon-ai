"""Ollama LLM provider (local, free)."""

import httpx

from pokemon_ai.config import settings
from pokemon_ai.llm.base import LLMProvider, LLMResponse, Message, ToolCall
from pokemon_ai.llm.rate_limiter import get_rate_limiter


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider with vision support."""

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self._limiter = get_rate_limiter("ollama")

    def name(self) -> str:
        return f"ollama/{self.model}"

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        await self._limiter.acquire()

        ollama_messages = []
        for msg in messages:
            m: dict = {"role": msg.role, "content": msg.content}
            if msg.image_b64:
                m["images"] = [msg.image_b64]
            ollama_messages.append(m)

        payload: dict = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        message = data.get("message", {})
        content = message.get("content")

        tool_calls = []
        for tc in message.get("tool_calls", []):
            func = tc.get("function", {})
            tool_calls.append(ToolCall(
                id=func.get("name", ""),
                name=func.get("name", ""),
                arguments=func.get("arguments", {}),
            ))

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
        )
