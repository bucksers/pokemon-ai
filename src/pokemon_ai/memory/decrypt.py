"""Gen III Pokemon data substructure decryption.

In Generation III, each Pokemon's 48-byte data block is encrypted and split into
4 substructures of 12 bytes each. The order of substructures depends on
personality_value % 24.

Substructures:
  G (Growth):   species, item, experience, PP bonuses, friendship, etc.
  A (Attacks):  move1-4, pp1-4
  E (EVs):      HP/Atk/Def/Spd/SpA/SpD EVs + condition
  M (Misc):     pokerus, met location, origins, IVs, ability, ribbons

References:
  https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_substructures_(Generation_III)
"""

import struct
from dataclasses import dataclass

# The 24 possible substructure orderings indexed by personality_value % 24
SUBSTRUCTURE_ORDER = [
    "GAEM", "GAME", "GEAM", "GEMA", "GMAE", "GMEA",
    "AGEM", "AGME", "AEGM", "AEMG", "AMGE", "AMEG",
    "EGAM", "EGMA", "EAGM", "EAMG", "EMGA", "EMAG",
    "MGAE", "MGEA", "MAGE", "MAEG", "MEGA", "MEAG",
]


@dataclass
class GrowthSubstructure:
    species: int
    item: int
    experience: int
    pp_bonuses: int
    friendship: int


@dataclass
class AttacksSubstructure:
    move1: int
    move2: int
    move3: int
    move4: int
    pp1: int
    pp2: int
    pp3: int
    pp4: int


@dataclass
class EVsSubstructure:
    hp_ev: int
    attack_ev: int
    defense_ev: int
    speed_ev: int
    sp_atk_ev: int
    sp_def_ev: int


@dataclass
class MiscSubstructure:
    pokerus: int
    met_location: int
    origins_info: int
    iv_egg_ability: int  # packed IVs, egg flag, ability bit


def decrypt_data_block(data_block: bytes, personality: int, ot_id: int) -> bytes:
    """Decrypt the 48-byte data block using personality XOR ot_id as the key.

    Each 4-byte word in the block is XORed with the key.
    """
    key = personality ^ ot_id
    decrypted = bytearray(48)
    for i in range(0, 48, 4):
        word = struct.unpack_from("<I", data_block, i)[0]
        word ^= key
        struct.pack_into("<I", decrypted, i, word)
    return bytes(decrypted)


def get_substructure_positions(personality: int) -> dict[str, int]:
    """Get the byte offset for each substructure (G, A, E, M) within the decrypted block."""
    order = SUBSTRUCTURE_ORDER[personality % 24]
    return {letter: idx * 12 for idx, letter in enumerate(order)}


def parse_growth(data: bytes) -> GrowthSubstructure:
    """Parse the Growth substructure from 12 bytes."""
    species, item, experience, pp_bonuses, friendship = struct.unpack_from("<HHIBBxx", data)
    return GrowthSubstructure(
        species=species,
        item=item,
        experience=experience,
        pp_bonuses=pp_bonuses,
        friendship=friendship,
    )


def parse_attacks(data: bytes) -> AttacksSubstructure:
    """Parse the Attacks substructure from 12 bytes."""
    m1, m2, m3, m4, pp1, pp2, pp3, pp4 = struct.unpack_from("<HHHHBBBB", data)
    return AttacksSubstructure(
        move1=m1, move2=m2, move3=m3, move4=m4,
        pp1=pp1, pp2=pp2, pp3=pp3, pp4=pp4,
    )


def parse_evs(data: bytes) -> EVsSubstructure:
    """Parse the EVs substructure from 12 bytes."""
    hp, atk, dfn, spd, spa, spd2 = struct.unpack_from("<BBBBBBxx", data)
    return EVsSubstructure(
        hp_ev=hp, attack_ev=atk, defense_ev=dfn,
        speed_ev=spd, sp_atk_ev=spa, sp_def_ev=spd2,
    )


def parse_misc(data: bytes) -> MiscSubstructure:
    """Parse the Misc substructure from 12 bytes."""
    pokerus, met_loc, origins, iv_data = struct.unpack_from("<BBHI", data)
    return MiscSubstructure(
        pokerus=pokerus,
        met_location=met_loc,
        origins_info=origins,
        iv_egg_ability=iv_data,
    )


def extract_ivs(iv_egg_ability: int) -> dict[str, int]:
    """Extract individual IVs from the packed 32-bit value."""
    return {
        "hp": iv_egg_ability & 0x1F,
        "attack": (iv_egg_ability >> 5) & 0x1F,
        "defense": (iv_egg_ability >> 10) & 0x1F,
        "speed": (iv_egg_ability >> 15) & 0x1F,
        "sp_atk": (iv_egg_ability >> 20) & 0x1F,
        "sp_def": (iv_egg_ability >> 25) & 0x1F,
    }


def decrypt_pokemon(raw_data: bytes, personality: int, ot_id: int) -> tuple[
    GrowthSubstructure, AttacksSubstructure, EVsSubstructure, MiscSubstructure
]:
    """Fully decrypt and parse a Pokemon's 48-byte data block into all 4 substructures."""
    decrypted = decrypt_data_block(raw_data, personality, ot_id)
    positions = get_substructure_positions(personality)

    growth = parse_growth(decrypted[positions["G"]:positions["G"] + 12])
    attacks = parse_attacks(decrypted[positions["A"]:positions["A"] + 12])
    evs = parse_evs(decrypted[positions["E"]:positions["E"] + 12])
    misc = parse_misc(decrypted[positions["M"]:positions["M"] + 12])

    return growth, attacks, evs, misc
