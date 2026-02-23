"""Tests for tool definitions."""

from pokemon_ai.llm.tools import TOOLS, TOOL_NAMES


class TestToolDefinitions:
    def test_all_tools_have_required_fields(self):
        for tool in TOOLS:
            assert tool["type"] == "function"
            func = tool["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func

    def test_tool_names(self):
        assert "press_button" in TOOL_NAMES
        assert "press_sequence" in TOOL_NAMES
        assert "wait" in TOOL_NAMES

    def test_press_button_has_valid_enum(self):
        tool = next(t for t in TOOLS if t["function"]["name"] == "press_button")
        button_enum = tool["function"]["parameters"]["properties"]["button"]["enum"]
        assert "A" in button_enum
        assert "B" in button_enum
        assert "UP" in button_enum
        assert "START" in button_enum


class TestToolFormat:
    def test_openai_compatible_format(self):
        """Tools should be in OpenAI-compatible format."""
        for tool in TOOLS:
            assert "type" in tool
            assert "function" in tool
            func = tool["function"]
            assert "name" in func
            params = func["parameters"]
            assert params["type"] == "object"
