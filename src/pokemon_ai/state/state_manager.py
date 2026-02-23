"""Assemble complete GameState from memory reads + screenshot."""

from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.emulator.screenshot import png_to_base64, resize_screenshot
from pokemon_ai.memory.battle import read_battle_state
from pokemon_ai.memory.party import read_party
from pokemon_ai.memory.player import read_player
from pokemon_ai.state.game_state import GameMode, GameState
from pokemon_ai.state.mode_detector import detect_mode


class StateManager:
    """Reads and assembles the complete game state."""

    def __init__(self, client: EmulatorClient):
        self.client = client

    async def get_state(self, include_screenshot: bool = True) -> GameState:
        """Read the full game state from the emulator."""
        mode = await detect_mode(self.client)

        state = GameState(mode=mode)

        # Always try to read player and party
        try:
            state.player = await read_player(self.client)
        except Exception:
            pass

        try:
            state.party = await read_party(self.client)
        except Exception:
            state.party = []

        # Read battle state if in battle
        if mode == GameMode.BATTLE:
            try:
                result = await read_battle_state(self.client)
                if result:
                    state.battle_player, state.battle_enemy = result
            except Exception:
                pass

        # Capture screenshot
        if include_screenshot:
            try:
                png = await self.client.screenshot()
                png = resize_screenshot(png)
                state.screenshot_b64 = png_to_base64(png)
            except Exception:
                pass

        return state
