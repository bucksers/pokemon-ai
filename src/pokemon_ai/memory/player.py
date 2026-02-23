"""Parse player state from RAM."""

from dataclasses import dataclass

from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.memory.addresses import (
    BADGE_FLAG_START,
    MONEY_OFFSET,
    PLAYER_FACING,
    PLAYER_MAP_GROUP,
    PLAYER_MAP_NUMBER,
    PLAYER_X,
    PLAYER_Y,
    SAVE_BLOCK_1_PTR,
    SAVE_BLOCK_2_PTR,
    TRAINER_ID_OFFSET,
    TRAINER_NAME_OFFSET,
)
from pokemon_ai.memory.reader import read_pointer, read_string, read_u16, read_u32, read_u8


@dataclass
class PlayerState:
    """Current player state."""
    name: str
    trainer_id: int
    x: int
    y: int
    map_group: int
    map_number: int
    facing: int  # 1=down, 2=up, 3=left, 4=right
    badges: list[bool]  # 8 badges
    money: int

    @property
    def badge_count(self) -> int:
        return sum(self.badges)

    @property
    def facing_str(self) -> str:
        return {1: "down", 2: "up", 3: "left", 4: "right"}.get(self.facing, "unknown")


async def read_player(client: EmulatorClient) -> PlayerState:
    """Read player state from RAM."""
    sb1 = await read_pointer(client, SAVE_BLOCK_1_PTR)
    sb2 = await read_pointer(client, SAVE_BLOCK_2_PTR)

    name = await read_string(client, sb2 + TRAINER_NAME_OFFSET, 8)
    trainer_id = await read_u32(client, sb2 + TRAINER_ID_OFFSET)

    x = await read_u16(client, PLAYER_X)
    y = await read_u16(client, PLAYER_Y)
    map_group = await read_u8(client, PLAYER_MAP_GROUP)
    map_number = await read_u8(client, PLAYER_MAP_NUMBER)
    facing = await read_u8(client, PLAYER_FACING)

    # Read badges (each is a flag bit)
    # In FireRed, badges are stored as flag bits
    badges = []
    for i in range(8):
        flag_byte_offset = (BADGE_FLAG_START + i) // 8
        flag_bit = (BADGE_FLAG_START + i) % 8
        byte_val = await read_u8(client, sb1 + 0x0EE0 + flag_byte_offset)
        badges.append(bool(byte_val & (1 << flag_bit)))

    # Money (encrypted with trainer ID in FireRed)
    money_raw = await read_u32(client, sb1 + MONEY_OFFSET)
    money_key = await read_u32(client, sb1 + MONEY_OFFSET + 4)
    money = money_raw ^ money_key

    return PlayerState(
        name=name,
        trainer_id=trainer_id,
        x=x,
        y=y,
        map_group=map_group,
        map_number=map_number,
        facing=facing,
        badges=badges,
        money=money,
    )
