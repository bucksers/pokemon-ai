"""Tests for prompt generation."""

from pokemon_ai.agent.prompts import get_system_prompt, MODE_PROMPTS


class TestPrompts:
    def test_all_modes_have_prompts(self):
        for mode in ["overworld", "battle", "menu", "dialogue"]:
            assert mode in MODE_PROMPTS

    def test_system_prompt_includes_base(self):
        prompt = get_system_prompt("battle")
        assert "Pokemon FireRed" in prompt
        assert "BATTLE" in prompt

    def test_battle_prompt_has_menu_layout(self):
        prompt = get_system_prompt("battle")
        assert "FIGHT" in prompt
        assert "BAG" in prompt
        assert "top-left" in prompt

    def test_unknown_mode_defaults_to_overworld(self):
        prompt = get_system_prompt("unknown")
        assert "OVERWORLD" in prompt
