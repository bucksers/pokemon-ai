"""Tests for action history ring buffer."""

from pokemon_ai.agent.history import ActionHistory


class TestActionHistory:
    def test_add_and_retrieve(self):
        h = ActionHistory(max_size=5)
        h.add("press_button A")
        assert len(h) == 1
        assert h.recent[0].action == "press_button A"

    def test_max_size(self):
        h = ActionHistory(max_size=3)
        for i in range(5):
            h.add(f"action_{i}")
        assert len(h) == 3
        assert h.recent[0].action == "action_2"

    def test_last_n(self):
        h = ActionHistory()
        for i in range(15):
            h.add(f"action_{i}")
        assert len(h.last_n) == 10

    def test_is_stuck_true(self):
        h = ActionHistory()
        for _ in range(10):
            h.add("press_button A")
        assert h.is_stuck()

    def test_is_stuck_false_varied(self):
        h = ActionHistory()
        for btn in ["A", "B", "UP", "DOWN", "LEFT", "RIGHT", "A", "B", "UP", "DOWN"]:
            h.add(f"press_button {btn}")
        assert not h.is_stuck()

    def test_is_stuck_not_enough_data(self):
        h = ActionHistory()
        h.add("press_button A")
        assert not h.is_stuck()

    def test_format_for_prompt_empty(self):
        h = ActionHistory()
        assert "No actions" in h.format_for_prompt()

    def test_format_for_prompt_with_data(self):
        h = ActionHistory()
        h.add("press_button A")
        h.add("press_button UP")
        output = h.format_for_prompt()
        assert "press_button A" in output
        assert "press_button UP" in output


class TestStuckDetection:
    def test_two_alternating_actions_is_stuck(self):
        """Alternating between 2 actions should also count as stuck."""
        h = ActionHistory()
        for _ in range(5):
            h.add("press_button A")
            h.add("press_button B")
        assert h.is_stuck()
