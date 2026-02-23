"""Unified game state dataclass."""

from dataclasses import dataclass, field
from enum import Enum

from pokemon_ai.memory.battle import BattleMon
from pokemon_ai.memory.party import PartyPokemon
from pokemon_ai.memory.player import PlayerState


class GameMode(str, Enum):
    OVERWORLD = "overworld"
    BATTLE = "battle"
    MENU = "menu"
    DIALOGUE = "dialogue"
    UNKNOWN = "unknown"


@dataclass
class GameState:
    """Complete snapshot of the current game state."""
    mode: GameMode
    player: PlayerState | None = None
    party: list[PartyPokemon] = field(default_factory=list)
    battle_player: BattleMon | None = None
    battle_enemy: BattleMon | None = None
    screenshot_b64: str | None = None

    @property
    def in_battle(self) -> bool:
        return self.mode == GameMode.BATTLE

    @property
    def alive_party_count(self) -> int:
        return sum(1 for p in self.party if not p.is_fainted)

    def summary(self) -> str:
        """Human-readable summary of the game state."""
        lines = [f"Mode: {self.mode.value}"]

        if self.player:
            p = self.player
            lines.append(f"Player: {p.name} @ ({p.x}, {p.y}) facing {p.facing_str}")
            lines.append(f"Badges: {p.badge_count}/8 | Money: ${p.money}")

        if self.party:
            lines.append(f"Party ({len(self.party)}):")
            for mon in self.party:
                status = " [FNT]" if mon.is_fainted else ""
                lines.append(
                    f"  {mon.nickname} (#{mon.species_id}) "
                    f"Lv{mon.level} HP:{mon.current_hp}/{mon.max_hp}{status}"
                )

        if self.in_battle and self.battle_player and self.battle_enemy:
            lines.append("--- BATTLE ---")
            bp = self.battle_player
            be = self.battle_enemy
            lines.append(
                f"  Player: #{bp.species_id} Lv{bp.level} "
                f"HP:{bp.current_hp}/{bp.max_hp}"
            )
            lines.append(
                f"  Enemy:  #{be.species_id} Lv{be.level} "
                f"HP:{be.current_hp}/{be.max_hp}"
            )

        return "\n".join(lines)
