"""Tests for move data lookups."""

from pokemon_ai.knowledge.moves import get_move, get_move_name


class TestMoveLookup:
    def test_known_move(self):
        move = get_move(85)  # Thunderbolt
        assert move is not None
        assert move.name == "Thunderbolt"
        assert move.type == "Electric"
        assert move.power == 95
        assert move.damage_class == "special"

    def test_status_move(self):
        move = get_move(86)  # Thunder Wave
        assert move is not None
        assert move.power is None
        assert move.damage_class == "status"

    def test_priority_move(self):
        move = get_move(98)  # Quick Attack
        assert move is not None
        assert move.priority == 1

    def test_unknown_move(self):
        assert get_move(9999) is None

    def test_get_move_name(self):
        assert get_move_name(53) == "Flamethrower"
        assert get_move_name(9999) == "Move#9999"
