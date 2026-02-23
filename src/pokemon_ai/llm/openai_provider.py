"""OpenAI LLM provider."""

import json

import openai

from pokemon_ai.config import settings
from pokemon_ai.llm.base import LLMProvider, LLMResponse, Message, ToolCall
from pokemon_ai.llm.rate_limiter import get_rate_limiter


class OpenAIProvider(LLMProvider):
    """OpenAI provider with vision and tool support."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self._limiter = get_rate_limiter("openai")
        self._client = openai.AsyncOpenAI(api_key=self.api_key)

    def name(self) -> str:
        return f"openai/{self.model}"

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        await self._limiter.acquire()

        oai_messages = []
        for msg in messages:
            if msg.role == "tool":
                oai_messages.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": msg.content,
                })
                continue

            if msg.image_b64:
                oai_messages.append({
                    "role": msg.role,
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{msg.image_b64}",
                                "detail": "low",
                            },
                        },
                        {"type": "text", "text": msg.content or ""},
                    ],
                })
            else:
                oai_messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        kwargs: dict = {
            "model": self.model,
            "messages": oai_messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        content = choice.message.content
        tool_calls = []

        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                ))

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            } if response.usage else None,
        )
