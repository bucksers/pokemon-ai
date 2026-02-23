"""Tests for base LLM types."""

from pokemon_ai.llm.base import LLMResponse, Message, ToolCall


class TestMessage:
    def test_basic_message(self):
        msg = Message(role="user", content="hello")
        assert msg.role == "user"
        assert msg.content == "hello"
        assert msg.image_b64 is None

    def test_message_with_image(self):
        msg = Message(role="user", content="what's on screen?", image_b64="abc123")
        assert msg.image_b64 == "abc123"


class TestLLMResponse:
    def test_no_tool_calls(self):
        resp = LLMResponse(content="I'll press A")
        assert not resp.has_tool_calls
        assert resp.content == "I'll press A"

    def test_with_tool_calls(self):
        resp = LLMResponse(
            tool_calls=[ToolCall(id="1", name="press_button", arguments={"button": "A"})]
        )
        assert resp.has_tool_calls
        assert resp.tool_calls[0].name == "press_button"
