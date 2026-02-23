"""Parse party Pokemon from RAM."""

import struct
from dataclasses import dataclass

from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.memory.addresses import (
    MAX_PARTY_SIZE,
    PARTY_COUNT_OFFSET,
    PARTY_DATA_OFFSET,
    PKM_ATTACK,
    PKM_CURRENT_HP,
    PKM_DATA,
    PKM_DEFENSE,
    PKM_LEVEL,
    PKM_MAX_HP,
    PKM_NICKNAME,
    PKM_OT_ID,
    PKM_PERSONALITY,
    PKM_SP_ATK,
    PKM_SP_DEF,
    PKM_SPEED,
    PKM_STATUS,
    POKEMON_DATA_SIZE,
    SAVE_BLOCK_1_PTR,
)
from pokemon_ai.memory.decrypt import decrypt_pokemon
from pokemon_ai.memory.reader import decode_gen3_string, read_pointer


@dataclass
class PartyPokemon:
    """Parsed party Pokemon data."""
    species_id: int
    nickname: str
    level: int
    current_hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    sp_atk: int
    sp_def: int
    status: int
    moves: list[int]  # move IDs (up to 4)
    pp: list[int]  # PP for each move
    item: int
    experience: int
    friendship: int
    personality: int

    @property
    def is_fainted(self) -> bool:
        return self.current_hp == 0

    @property
    def hp_percent(self) -> float:
        if self.max_hp == 0:
            return 0.0
        return self.current_hp / self.max_hp * 100


def parse_party_pokemon(raw: bytes) -> PartyPokemon | None:
    """Parse a single party Pokemon from its 100-byte structure."""
    if len(raw) < POKEMON_DATA_SIZE:
        return None

    personality = struct.unpack_from("<I", raw, PKM_PERSONALITY)[0]
    ot_id = struct.unpack_from("<I", raw, PKM_OT_ID)[0]

    # A personality of 0 means empty slot
    if personality == 0:
        return None

    nickname = decode_gen3_string(raw[PKM_NICKNAME:PKM_NICKNAME + 10])

    # Decrypt the 48-byte data block
    data_block = raw[PKM_DATA:PKM_DATA + 48]
    growth, attacks, evs, misc = decrypt_pokemon(data_block, personality, ot_id)

    # Species 0 means empty
    if growth.species == 0:
        return None

    # Read calculated stats from the party data section (bytes 0x50+)
    status = struct.unpack_from("<I", raw, PKM_STATUS)[0]
    level = raw[PKM_LEVEL]
    current_hp = struct.unpack_from("<H", raw, PKM_CURRENT_HP)[0]
    max_hp = struct.unpack_from("<H", raw, PKM_MAX_HP)[0]
    attack = struct.unpack_from("<H", raw, PKM_ATTACK)[0]
    defense = struct.unpack_from("<H", raw, PKM_DEFENSE)[0]
    speed = struct.unpack_from("<H", raw, PKM_SPEED)[0]
    sp_atk = struct.unpack_from("<H", raw, PKM_SP_ATK)[0]
    sp_def = struct.unpack_from("<H", raw, PKM_SP_DEF)[0]

    moves = [attacks.move1, attacks.move2, attacks.move3, attacks.move4]
    moves = [m for m in moves if m != 0]
    pp = [attacks.pp1, attacks.pp2, attacks.pp3, attacks.pp4][:len(moves)]

    return PartyPokemon(
        species_id=growth.species,
        nickname=nickname,
        level=level,
        current_hp=current_hp,
        max_hp=max_hp,
        attack=attack,
        defense=defense,
        speed=speed,
        sp_atk=sp_atk,
        sp_def=sp_def,
        status=status,
        moves=moves,
        pp=pp,
        item=growth.item,
        experience=growth.experience,
        friendship=growth.friendship,
        personality=personality,
    )


async def read_party(client: EmulatorClient) -> list[PartyPokemon]:
    """Read the full party from RAM."""
    sb1 = await read_pointer(client, SAVE_BLOCK_1_PTR)
    party_count_addr = sb1 + PARTY_COUNT_OFFSET
    party_data_addr = sb1 + PARTY_DATA_OFFSET

    count = await client.read_byte(party_count_addr)
    count = min(count, MAX_PARTY_SIZE)

    if count == 0:
        return []

    raw = await client.read_bytes(party_data_addr, count * POKEMON_DATA_SIZE)
    party = []
    for i in range(count):
        offset = i * POKEMON_DATA_SIZE
        mon = parse_party_pokemon(raw[offset:offset + POKEMON_DATA_SIZE])
        if mon is not None:
            party.append(mon)

    return party
