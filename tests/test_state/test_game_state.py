"""Tests for GameState and mode detection logic."""

from pokemon_ai.memory.party import PartyPokemon
from pokemon_ai.state.game_state import GameMode, GameState


class TestGameState:
    def test_default_state(self):
        state = GameState(mode=GameMode.OVERWORLD)
        assert state.mode == GameMode.OVERWORLD
        assert state.party == []
        assert not state.in_battle

    def test_in_battle(self):
        state = GameState(mode=GameMode.BATTLE)
        assert state.in_battle

    def test_alive_party_count(self):
        mon1 = PartyPokemon(
            species_id=25, nickname="Pikachu", level=15,
            current_hp=35, max_hp=35, attack=30, defense=20,
            speed=50, sp_atk=35, sp_def=30, status=0,
            moves=[84, 98], pp=[30, 30], item=0,
            experience=1000, friendship=70, personality=12345,
        )
        mon2 = PartyPokemon(
            species_id=1, nickname="Bulbasaur", level=10,
            current_hp=0, max_hp=30, attack=25, defense=25,
            speed=20, sp_atk=30, sp_def=30, status=0,
            moves=[33, 45], pp=[35, 40], item=0,
            experience=500, friendship=70, personality=67890,
        )
        state = GameState(mode=GameMode.OVERWORLD, party=[mon1, mon2])
        assert state.alive_party_count == 1

    def test_summary_output(self):
        state = GameState(mode=GameMode.OVERWORLD)
        summary = state.summary()
        assert "overworld" in summary.lower()


class TestPartyPokemon:
    def test_is_fainted(self):
        mon = PartyPokemon(
            species_id=25, nickname="Pikachu", level=15,
            current_hp=0, max_hp=35, attack=30, defense=20,
            speed=50, sp_atk=35, sp_def=30, status=0,
            moves=[84], pp=[30], item=0,
            experience=1000, friendship=70, personality=12345,
        )
        assert mon.is_fainted

    def test_hp_percent(self):
        mon = PartyPokemon(
            species_id=25, nickname="Pikachu", level=15,
            current_hp=18, max_hp=35, attack=30, defense=20,
            speed=50, sp_atk=35, sp_def=30, status=0,
            moves=[84], pp=[30], item=0,
            experience=1000, friendship=70, personality=12345,
        )
        assert abs(mon.hp_percent - 51.43) < 0.1
