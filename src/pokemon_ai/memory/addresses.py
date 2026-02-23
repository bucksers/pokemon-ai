"""Pokemon FireRed RAM address constants.

Memory map references:
- https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_(Generation_III)
- https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_FireRed/RAM_map
"""

# ── Save block pointers ──
# FireRed uses a two-save-block system. These are the pointers to the current blocks.
SAVE_BLOCK_1_PTR = 0x03005008  # player data, party, items, etc.
SAVE_BLOCK_2_PTR = 0x0300500C  # game flags, vars, etc.

# ── Party Pokemon ──
# Offsets from SaveBlock1
PARTY_COUNT_OFFSET = 0x0034
PARTY_DATA_OFFSET = 0x0038
POKEMON_DATA_SIZE = 100  # each party Pokemon is 100 bytes
MAX_PARTY_SIZE = 6

# ── Player position ──
# These are direct RAM addresses (not save block offsets)
PLAYER_X = 0x02036E48  # current X position on map
PLAYER_Y = 0x02036E4A  # current Y position on map
PLAYER_MAP_GROUP = 0x02036E4E
PLAYER_MAP_NUMBER = 0x02036E4F
PLAYER_FACING = 0x02036E50  # direction player faces

# ── Trainer data ──
TRAINER_NAME_OFFSET = 0x0000  # from SaveBlock2
TRAINER_ID_OFFSET = 0x000A  # from SaveBlock2 (public + secret)
TRAINER_GENDER_OFFSET = 0x0008  # from SaveBlock2

# ── Badges + Money ──
BADGE_FLAG_START = 0x0820  # flag offset (from SaveBlock1) for badge 1
MONEY_OFFSET = 0x0290  # from SaveBlock1, encrypted with XOR key

# ── Battle state ──
# These are in EWRAM, not relative to save blocks
BATTLE_FLAG = 0x030030F0  # nonzero when in battle
BATTLE_OUTCOME = 0x0300431C

# Current battle Pokemon data
BATTLE_PLAYER_MON = 0x02023BE4  # active player Pokemon in battle (BattlePokemon struct)
BATTLE_ENEMY_MON = 0x02023C6C  # active enemy Pokemon in battle
BATTLE_MON_SIZE = 0x58  # size of BattlePokemon struct (88 bytes)

# ── Battle Pokemon struct offsets ──
# These are offsets within the BattlePokemon struct
BATTLE_MON_SPECIES = 0x00  # u16
BATTLE_MON_ATTACK = 0x02  # u16
BATTLE_MON_DEFENSE = 0x04  # u16
BATTLE_MON_SPEED = 0x06  # u16
BATTLE_MON_SP_ATK = 0x08  # u16
BATTLE_MON_SP_DEF = 0x0A  # u16
BATTLE_MON_MOVE1 = 0x0C  # u16
BATTLE_MON_MOVE2 = 0x0E  # u16
BATTLE_MON_MOVE3 = 0x10  # u16
BATTLE_MON_MOVE4 = 0x12  # u16
BATTLE_MON_PP1 = 0x24  # u8
BATTLE_MON_PP2 = 0x25  # u8
BATTLE_MON_PP3 = 0x26  # u8
BATTLE_MON_PP4 = 0x27  # u8
BATTLE_MON_HP = 0x28  # u16
BATTLE_MON_MAX_HP = 0x2A  # u16
BATTLE_MON_LEVEL = 0x2C  # u8
BATTLE_MON_STATUS = 0x4C  # u32 (status condition bitfield)

# ── Menu / Dialogue detection ──
# Callback pointers that indicate what the game is currently doing
CALLBACK1 = 0x030030F4
CALLBACK2 = 0x030030F8

# ── Bag items ──
BAG_ITEMS_OFFSET = 0x0310  # from SaveBlock1
BAG_ITEMS_COUNT = 42  # max items in regular pocket
BAG_ITEM_SIZE = 4  # item_id (u16) + quantity (u16)

# ── Gen III Pokemon data structure ──
# Each Pokemon in the party is 100 bytes:
#   0x00-0x03: Personality Value (u32)
#   0x04-0x07: OT ID (u32)
#   0x08-0x11: Nickname (10 bytes)
#   0x12-0x13: Language, flags
#   0x14-0x1D: OT Name (7 bytes)
#   0x1E:      Markings
#   0x1F:      Checksum padding
#   0x20-0x23: Checksum (u16) + padding
#   0x20-0x4F: 48 bytes of encrypted data (4 substructures x 12 bytes)
#   0x50-0x53: Status condition
#   0x54:      Level
#   0x55:      Pokerus
#   0x56-0x57: Current HP
#   0x58-0x59: Max HP
#   0x5A-0x5B: Attack
#   0x5C-0x5D: Defense
#   0x5E-0x5F: Speed
#   0x60-0x61: Sp. Attack
#   0x62-0x63: Sp. Defense

# Offsets within a party Pokemon structure
PKM_PERSONALITY = 0x00
PKM_OT_ID = 0x04
PKM_NICKNAME = 0x08
PKM_CHECKSUM = 0x1C
PKM_DATA = 0x20  # start of 48-byte encrypted block
PKM_STATUS = 0x50
PKM_LEVEL = 0x54
PKM_POKERUS = 0x55
PKM_CURRENT_HP = 0x56
PKM_MAX_HP = 0x58
PKM_ATTACK = 0x5A
PKM_DEFENSE = 0x5C
PKM_SPEED = 0x5E
PKM_SP_ATK = 0x60
PKM_SP_DEF = 0x62
