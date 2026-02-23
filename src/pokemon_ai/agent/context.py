"""Format game state and knowledge into LLM messages."""

from pokemon_ai.knowledge.moves import get_move_name, get_move
from pokemon_ai.knowledge.pokemon import get_pokemon_name
from pokemon_ai.knowledge.progression import get_current_step
from pokemon_ai.llm.base import Message
from pokemon_ai.state.game_state import GameState


def format_state_message(state: GameState, history_str: str) -> Message:
    """Build the user message with game state, knowledge, and screenshot."""
    parts = [f"GAME MODE: {state.mode.value}\n"]

    # Player info
    if state.player:
        p = state.player
        parts.append(f"PLAYER: {p.name} at ({p.x}, {p.y}) facing {p.facing_str}")
        parts.append(f"BADGES: {p.badge_count}/8 | MONEY: ${p.money}")

        # Current objective
        step = get_current_step(p.badge_count)
        parts.append(f"\nCURRENT OBJECTIVE: {step.name}")
        parts.append(f"  {step.objective}")

    # Party
    if state.party:
        parts.append(f"\nPARTY ({len(state.party)} Pokemon):")
        for mon in state.party:
            name = get_pokemon_name(mon.species_id)
            status = " [FAINTED]" if mon.is_fainted else ""
            parts.append(
                f"  {mon.nickname} ({name}) Lv{mon.level} "
                f"HP:{mon.current_hp}/{mon.max_hp}{status}"
            )
            move_strs = []
            for i, move_id in enumerate(mon.moves):
                move_name = get_move_name(move_id)
                pp = mon.pp[i] if i < len(mon.pp) else "?"
                move_strs.append(f"{move_name} (PP:{pp})")
            parts.append(f"    Moves: {', '.join(move_strs)}")

    # Battle context with type analysis
    if state.in_battle and state.battle_player and state.battle_enemy:
        bp = state.battle_player
        be = state.battle_enemy
        player_name = get_pokemon_name(bp.species_id)
        enemy_name = get_pokemon_name(be.species_id)

        parts.append("\nBATTLE STATE:")
        parts.append(
            f"  Your {player_name} Lv{bp.level}: "
            f"HP {bp.current_hp}/{bp.max_hp}"
        )
        parts.append(
            f"  Enemy {enemy_name} Lv{be.level}: "
            f"HP {be.current_hp}/{be.max_hp}"
        )

        # Move analysis with type effectiveness
        parts.append("\n  Your moves:")
        for i, move_id in enumerate(bp.moves):
            move = get_move(move_id)
            pp = bp.pp[i] if i < len(bp.pp) else 0
            if move:
                eff_note = ""
                if move.power and move.type:
                    # We don't know enemy types from RAM easily,
                    # but include move type for the LLM to reason about
                    eff_note = f" [{move.type}-type, {move.damage_class}]"
                parts.append(
                    f"    {i+1}. {move.name} - Power:{move.power or '-'} "
                    f"Acc:{move.accuracy or '-'} PP:{pp}{eff_note}"
                )
            else:
                parts.append(f"    {i+1}. Move#{move_id} PP:{pp}")

    # Recent actions
    parts.append(f"\nRECENT ACTIONS:\n{history_str}")

    parts.append("\nWhat should you do next? Use a tool to take an action.")

    content = "\n".join(parts)
    return Message(
        role="user",
        content=content,
        image_b64=state.screenshot_b64,
    )
