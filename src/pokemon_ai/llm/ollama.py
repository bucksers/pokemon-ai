"""Ollama LLM provider (local, free)."""

import json
import re

import httpx

from pokemon_ai.config import settings
from pokemon_ai.llm.base import LLMProvider, LLMResponse, Message, ToolCall
from pokemon_ai.llm.rate_limiter import get_rate_limiter


def _parse_tool_from_text(text: str) -> ToolCall | None:
    """Try to extract a tool call from plain text when model doesn't support tools natively.

    Looks for patterns like:
      press_button A
      press_button("A")
      {"name": "press_button", "arguments": {"button": "A"}}
      Action: press A
    """
    text = text.strip()

    # Try JSON parse first
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and "name" in obj:
            return ToolCall(
                id=obj["name"],
                name=obj["name"],
                arguments=obj.get("arguments", {}),
            )
    except (json.JSONDecodeError, KeyError):
        pass

    # Look for button mentions in text
    button_names = {"A", "B", "UP", "DOWN", "LEFT", "RIGHT", "START", "SELECT", "L", "R"}

    # Pattern: "press A" or "press_button A" or "I'll press A"
    match = re.search(
        r'(?:press(?:_button)?|tap|hit|push)\s*\(?\s*["\']?(\w+)["\']?\s*\)?',
        text,
        re.IGNORECASE,
    )
    if match:
        button = match.group(1).upper()
        if button in button_names:
            return ToolCall(id="press_button", name="press_button", arguments={"button": button})

    # Pattern: just a button name on its own line
    for line in text.split("\n"):
        word = line.strip().upper()
        if word in button_names:
            return ToolCall(id="press_button", name="press_button", arguments={"button": word})

    # Pattern: "move up/down/left/right" or "go up"
    match = re.search(r'(?:move|go|walk|head)\s+(up|down|left|right)', text, re.IGNORECASE)
    if match:
        button = match.group(1).upper()
        return ToolCall(id="press_button", name="press_button", arguments={"button": button})

    return None


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

        # Most vision models don't support Ollama's tool format,
        # so we always use text mode and parse the response.
        if tools:
            tool_hint = (
                "\n\nRespond with ONLY the button to press. "
                "Valid buttons: A, B, UP, DOWN, LEFT, RIGHT, START, SELECT. "
                "Example: 'press A' or just 'A'. No other text."
            )
            for m in ollama_messages:
                if m["role"] == "system":
                    m["content"] += tool_hint
                    break

        payload: dict = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        message = data.get("message", {})
        content = message.get("content")

        # Parse native tool calls
        tool_calls = []
        for tc in message.get("tool_calls", []):
            func = tc.get("function", {})
            tool_calls.append(ToolCall(
                id=func.get("name", ""),
                name=func.get("name", ""),
                arguments=func.get("arguments", {}),
            ))

        # If no native tool calls, try parsing from text
        if not tool_calls and content:
            parsed = _parse_tool_from_text(content)
            if parsed:
                tool_calls.append(parsed)

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
            },
        )
