"""Tests for progression tracker."""

from pokemon_ai.knowledge.progression import get_current_step, load_progression


class TestProgression:
    def test_load_all_steps(self):
        steps = load_progression()
        assert len(steps) == 18
        assert steps[0].name == "Start in Pallet Town"
        assert steps[-1].name == "Elite Four & Champion"

    def test_zero_badges_early_game(self):
        step = get_current_step(0)
        assert step.step == 1

    def test_one_badge_post_brock(self):
        step = get_current_step(1)
        assert "Cerulean" in step.name or "Mt. Moon" in step.name

    def test_eight_badges_victory_road(self):
        step = get_current_step(8)
        assert "Victory" in step.name
