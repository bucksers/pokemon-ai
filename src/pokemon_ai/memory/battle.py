"""Parse battle state from RAM."""

import struct
from dataclasses import dataclass

from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.memory.addresses import (
    BATTLE_ENEMY_MON,
    BATTLE_FLAG,
    BATTLE_MON_DEFENSE,
    BATTLE_MON_HP,
    BATTLE_MON_LEVEL,
    BATTLE_MON_MAX_HP,
    BATTLE_MON_MOVE1,
    BATTLE_MON_PP1,
    BATTLE_MON_SIZE,
    BATTLE_MON_SP_ATK,
    BATTLE_MON_SP_DEF,
    BATTLE_MON_SPECIES,
    BATTLE_MON_SPEED,
    BATTLE_MON_STATUS,
    BATTLE_PLAYER_MON,
)
from pokemon_ai.memory.reader import read_u32


@dataclass
class BattleMon:
    """A Pokemon currently active in battle."""
    species_id: int
    level: int
    current_hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    sp_atk: int
    sp_def: int
    moves: list[int]
    pp: list[int]
    status: int

    @property
    def is_fainted(self) -> bool:
        return self.current_hp == 0

    @property
    def hp_percent(self) -> float:
        if self.max_hp == 0:
            return 0.0
        return self.current_hp / self.max_hp * 100


def parse_battle_mon(data: bytes) -> BattleMon:
    """Parse a BattlePokemon struct from raw bytes."""
    species = struct.unpack_from("<H", data, BATTLE_MON_SPECIES)[0]

    # Read stats (these are at offsets 0x02-0x0A)
    attack = struct.unpack_from("<H", data, 0x02)[0]
    defense = struct.unpack_from("<H", data, BATTLE_MON_DEFENSE)[0]
    speed = struct.unpack_from("<H", data, BATTLE_MON_SPEED)[0]
    sp_atk = struct.unpack_from("<H", data, BATTLE_MON_SP_ATK)[0]
    sp_def = struct.unpack_from("<H", data, BATTLE_MON_SP_DEF)[0]

    # Moves
    moves_raw = [
        struct.unpack_from("<H", data, BATTLE_MON_MOVE1 + i * 2)[0]
        for i in range(4)
    ]
    moves = [m for m in moves_raw if m != 0]

    # PP
    pp = [data[BATTLE_MON_PP1 + i] for i in range(len(moves))]

    hp = struct.unpack_from("<H", data, BATTLE_MON_HP)[0]
    max_hp = struct.unpack_from("<H", data, BATTLE_MON_MAX_HP)[0]
    level = data[BATTLE_MON_LEVEL]
    status = struct.unpack_from("<I", data, BATTLE_MON_STATUS)[0]

    return BattleMon(
        species_id=species,
        level=level,
        current_hp=hp,
        max_hp=max_hp,
        attack=attack,
        defense=defense,
        speed=speed,
        sp_atk=sp_atk,
        sp_def=sp_def,
        moves=moves,
        pp=pp,
        status=status,
    )


async def is_in_battle(client: EmulatorClient) -> bool:
    """Check if the game is currently in a battle."""
    flag = await read_u32(client, BATTLE_FLAG)
    return flag != 0


async def read_battle_state(client: EmulatorClient) -> tuple[BattleMon, BattleMon] | None:
    """Read the current battle state (player mon + enemy mon).

    Returns None if not in battle.
    """
    if not await is_in_battle(client):
        return None

    player_data = await client.read_bytes(BATTLE_PLAYER_MON, BATTLE_MON_SIZE)
    enemy_data = await client.read_bytes(BATTLE_ENEMY_MON, BATTLE_MON_SIZE)

    player = parse_battle_mon(player_data)
    enemy = parse_battle_mon(enemy_data)

    return player, enemy
