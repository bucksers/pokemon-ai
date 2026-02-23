"""Anthropic Claude LLM provider."""

import anthropic

from pokemon_ai.config import settings
from pokemon_ai.llm.base import LLMProvider, LLMResponse, Message, ToolCall
from pokemon_ai.llm.rate_limiter import get_rate_limiter


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider with vision and tool support."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.claude_model
        self._limiter = get_rate_limiter("claude")
        self._client = anthropic.AsyncAnthropic(api_key=self.api_key)

    def name(self) -> str:
        return f"claude/{self.model}"

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert OpenAI-format tools to Anthropic format."""
        return [
            {
                "name": t["function"]["name"],
                "description": t["function"].get("description", ""),
                "input_schema": t["function"].get("parameters", {"type": "object"}),
            }
            for t in tools
        ]

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        await self._limiter.acquire()

        system = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system = msg.content
                continue

            if msg.role == "tool":
                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_call_id,
                        "content": msg.content,
                    }],
                })
                continue

            content = []
            if msg.image_b64:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": msg.image_b64,
                    },
                })
            if msg.content:
                content.append({"type": "text", "text": msg.content})

            anthropic_messages.append({
                "role": msg.role,
                "content": content if len(content) > 1 else msg.content,
            })

        kwargs: dict = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": anthropic_messages,
            "temperature": temperature,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        response = await self._client.messages.create(**kwargs)

        content_text = None
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content_text = block.text
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input,
                ))

        return LLMResponse(
            content=content_text,
            tool_calls=tool_calls,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
            },
        )
