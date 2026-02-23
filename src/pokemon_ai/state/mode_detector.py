"""Detect the current game mode (overworld, battle, menu, dialogue)."""

from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.memory.addresses import BATTLE_FLAG, CALLBACK2
from pokemon_ai.memory.reader import read_u32
from pokemon_ai.state.game_state import GameMode

# Known callback addresses for FireRed (US v1.0)
# These are function pointers the game sets to control what's displayed
BATTLE_CALLBACKS = {
    0x0800F104,  # BattleMainCB2
    0x0800F0D0,  # sub_800F0D0 (battle transition)
}

OVERWORLD_CALLBACKS = {
    0x0805565C,  # CB2_Overworld
    0x08055668,  # CB2_OverworldBasic
}

MENU_CALLBACKS = {
    0x0809FA7C,  # CB2_StartMenu
    0x080A0FD0,  # CB2_BagMenuFromBattle
    0x080A1988,  # CB2_PartyMenu
}


async def detect_mode(client: EmulatorClient) -> GameMode:
    """Detect the current game mode from RAM state."""
    # Most reliable: check battle flag
    battle_flag = await read_u32(client, BATTLE_FLAG)
    if battle_flag != 0:
        return GameMode.BATTLE

    # Check callback2 for additional context
    cb2 = await read_u32(client, CALLBACK2)

    if cb2 in BATTLE_CALLBACKS:
        return GameMode.BATTLE
    if cb2 in MENU_CALLBACKS:
        return GameMode.MENU
    if cb2 in OVERWORLD_CALLBACKS:
        return GameMode.OVERWORLD

    # Fallback: if we have a valid callback but don't recognize it,
    # assume overworld (most common state)
    if cb2 != 0:
        return GameMode.OVERWORLD

    return GameMode.UNKNOWN
