"""Google Gemini LLM provider."""

import base64

from google import genai
from google.genai import types

from pokemon_ai.config import settings
from pokemon_ai.llm.base import LLMProvider, LLMResponse, Message, ToolCall
from pokemon_ai.llm.rate_limiter import get_rate_limiter


class GeminiProvider(LLMProvider):
    """Google Gemini provider with vision and tool support."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self._limiter = get_rate_limiter("gemini")
        self._client = genai.Client(api_key=self.api_key)

    def name(self) -> str:
        return f"gemini/{self.model}"

    def _build_tools(self, tools: list[dict]) -> list[types.Tool]:
        """Convert OpenAI-format tools to Gemini format."""
        declarations = []
        for tool in tools:
            func = tool["function"]
            declarations.append(types.FunctionDeclaration(
                name=func["name"],
                description=func.get("description", ""),
                parameters=func.get("parameters"),
            ))
        return [types.Tool(function_declarations=declarations)]

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        await self._limiter.acquire()

        # Build contents
        contents = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
                continue

            parts = []
            if msg.content:
                parts.append(types.Part.from_text(text=msg.content))
            if msg.image_b64:
                image_bytes = base64.b64decode(msg.image_b64)
                parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))

            role = "model" if msg.role == "assistant" else "user"
            contents.append(types.Content(role=role, parts=parts))

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction,
        )
        if tools:
            config.tools = self._build_tools(tools)

        response = await self._client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        # Parse response
        content = None
        tool_calls = []

        if response.candidates:
            candidate = response.candidates[0]
            for part in candidate.content.parts:
                if part.text:
                    content = part.text
                if part.function_call:
                    fc = part.function_call
                    tool_calls.append(ToolCall(
                        id=fc.name,
                        name=fc.name,
                        arguments=dict(fc.args) if fc.args else {},
                    ))

        usage = None
        if response.usage_metadata:
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
            }

        return LLMResponse(content=content, tool_calls=tool_calls, usage=usage)
