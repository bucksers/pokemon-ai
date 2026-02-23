"""Tests for type effectiveness lookups."""

from pokemon_ai.knowledge.types import (
    effectiveness,
    dual_effectiveness,
    get_immunities,
    get_resistances,
    get_weaknesses,
)


class TestEffectiveness:
    def test_super_effective(self):
        assert effectiveness("Fire", "Grass") == 2.0
        assert effectiveness("Water", "Fire") == 2.0
        assert effectiveness("Electric", "Water") == 2.0

    def test_not_very_effective(self):
        assert effectiveness("Fire", "Water") == 0.5
        assert effectiveness("Grass", "Fire") == 0.5

    def test_immune(self):
        assert effectiveness("Normal", "Ghost") == 0.0
        assert effectiveness("Electric", "Ground") == 0.0
        assert effectiveness("Ground", "Flying") == 0.0

    def test_neutral(self):
        assert effectiveness("Fire", "Normal") == 1.0
        assert effectiveness("Normal", "Normal") == 1.0

    def test_case_insensitive(self):
        assert effectiveness("fire", "grass") == 2.0
        assert effectiveness("FIRE", "GRASS") == 2.0

    def test_unknown_type_returns_neutral(self):
        assert effectiveness("Fairy", "Normal") == 1.0


class TestDualEffectiveness:
    def test_double_super_effective(self):
        # Fire vs Grass/Bug = 2.0 * 2.0 = 4.0
        assert dual_effectiveness("Fire", ["Grass", "Bug"]) == 4.0

    def test_super_and_resist_cancel(self):
        # Water vs Fire/Dragon = 2.0 * 0.5 = 1.0
        assert dual_effectiveness("Water", ["Fire", "Dragon"]) == 1.0

    def test_immunity_overrides_all(self):
        # Ground vs Water/Flying = 2.0 * 0.0 = 0.0
        assert dual_effectiveness("Ground", ["Water", "Flying"]) == 0.0


class TestWeaknessesAndResistances:
    def test_fire_weaknesses(self):
        weaknesses = get_weaknesses("Fire")
        assert "Water" in weaknesses
        assert "Ground" in weaknesses
        assert "Rock" in weaknesses

    def test_normal_immunities(self):
        immunities = get_immunities("Normal")
        assert "Ghost" in immunities

    def test_steel_resistances(self):
        resistances = get_resistances("Steel")
        assert len(resistances) > 0
