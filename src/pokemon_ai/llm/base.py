"""Abstract LLM provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Message:
    """A message in the conversation."""
    role: str  # "system", "user", "assistant", "tool"
    content: str
    image_b64: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None


@dataclass
class ToolCall:
    """A tool call returned by the LLM."""
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: dict | None = None  # token counts

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Send a chat completion request.

        Args:
            messages: Conversation messages.
            tools: Tool definitions in OpenAI-compatible format.
            temperature: Sampling temperature.

        Returns:
            LLMResponse with content and/or tool calls.
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """Provider name for logging."""
        ...
