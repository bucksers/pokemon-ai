"""Move database lookups.

Move data can be loaded from data/moves.json (fetched from PokeAPI)
or looked up by ID from a built-in subset of important Gen I-III moves.
"""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


@dataclass
class MoveData:
    id: int
    name: str
    type: str
    power: int | None
    accuracy: int | None
    pp: int
    damage_class: str  # "physical", "special", "status"
    priority: int = 0


# Built-in subset of commonly encountered moves (Gen III IDs)
BUILTIN_MOVES: dict[int, MoveData] = {
    1:   MoveData(1,   "Pound",        "Normal",   40,  100, 35, "physical"),
    5:   MoveData(5,   "Mega Punch",   "Normal",   80,  85,  20, "physical"),
    7:   MoveData(7,   "Fire Punch",   "Fire",     75,  100, 15, "physical"),
    8:   MoveData(8,   "Ice Punch",    "Ice",      75,  100, 15, "physical"),
    9:   MoveData(9,   "Thunder Punch","Electric", 75,  100, 15, "physical"),
    10:  MoveData(10,  "Scratch",      "Normal",   40,  100, 35, "physical"),
    13:  MoveData(13,  "Razor Wind",   "Normal",   80,  100, 10, "special"),
    14:  MoveData(14,  "Swords Dance", "Normal",   None,None, 30, "status"),
    15:  MoveData(15,  "Cut",          "Normal",   50,  95,  30, "physical"),
    16:  MoveData(16,  "Gust",         "Flying",   40,  100, 35, "special"),
    17:  MoveData(17,  "Wing Attack",  "Flying",   60,  100, 35, "physical"),
    22:  MoveData(22,  "Vine Whip",    "Grass",    35,  100, 15, "physical"),
    29:  MoveData(29,  "Headbutt",     "Normal",   70,  100, 15, "physical"),
    33:  MoveData(33,  "Tackle",       "Normal",   35,  95,  35, "physical"),
    36:  MoveData(36,  "Take Down",    "Normal",   90,  85,  20, "physical"),
    38:  MoveData(38,  "Double-Edge",  "Normal",   120, 100, 15, "physical"),
    45:  MoveData(45,  "Growl",        "Normal",   None,100, 40, "status"),
    47:  MoveData(47,  "Sing",         "Normal",   None,55,  15, "status"),
    52:  MoveData(52,  "Ember",        "Fire",     40,  100, 25, "special"),
    53:  MoveData(53,  "Flamethrower", "Fire",     95,  100, 15, "special"),
    55:  MoveData(55,  "Water Gun",    "Water",    40,  100, 25, "special"),
    56:  MoveData(56,  "Hydro Pump",   "Water",    120, 80,  5,  "special"),
    57:  MoveData(57,  "Surf",         "Water",    95,  100, 15, "special"),
    58:  MoveData(58,  "Ice Beam",     "Ice",      95,  100, 10, "special"),
    59:  MoveData(59,  "Blizzard",     "Ice",      120, 70,  5,  "special"),
    63:  MoveData(63,  "Hyper Beam",   "Normal",   150, 90,  5,  "special"),
    65:  MoveData(65,  "Drill Peck",   "Flying",   80,  100, 20, "physical"),
    72:  MoveData(72,  "Mega Drain",   "Grass",    40,  100, 15, "special"),
    73:  MoveData(73,  "Leech Seed",   "Grass",    None,90,  10, "status"),
    75:  MoveData(75,  "Razor Leaf",   "Grass",    55,  95,  25, "physical"),
    76:  MoveData(76,  "Solar Beam",   "Grass",    120, 100, 10, "special"),
    84:  MoveData(84,  "Thundershock", "Electric", 40,  100, 30, "special"),
    85:  MoveData(85,  "Thunderbolt",  "Electric", 95,  100, 15, "special"),
    86:  MoveData(86,  "Thunder Wave", "Electric", None,100, 20, "status"),
    87:  MoveData(87,  "Thunder",      "Electric", 120, 70,  10, "special"),
    89:  MoveData(89,  "Earthquake",   "Ground",   100, 100, 10, "physical"),
    92:  MoveData(92,  "Toxic",        "Poison",   None,85,  10, "status"),
    94:  MoveData(94,  "Psychic",      "Psychic",  90,  100, 10, "special"),
    98:  MoveData(98,  "Quick Attack", "Normal",   40,  100, 30, "physical", priority=1),
    104: MoveData(104, "Double Team",  "Normal",   None,None, 15, "status"),
    105: MoveData(105, "Recover",      "Normal",   None,None, 20, "status"),
    113: MoveData(113, "Light Screen", "Psychic",  None,None, 30, "status"),
    115: MoveData(115, "Reflect",      "Psychic",  None,None, 20, "status"),
    126: MoveData(126, "Fire Blast",   "Fire",     120, 85,  5,  "special"),
    129: MoveData(129, "Swift",        "Normal",   60,  None, 20, "special"),
    143: MoveData(143, "Sky Attack",   "Flying",   140, 90,  5,  "physical"),
    156: MoveData(156, "Rest",         "Psychic",  None,None, 10, "status"),
    157: MoveData(157, "Rock Slide",   "Rock",     75,  90,  10, "physical"),
    163: MoveData(163, "Slash",        "Normal",   70,  100, 20, "physical"),
    188: MoveData(188, "Sludge Bomb",  "Poison",   90,  100, 10, "special"),
    200: MoveData(200, "Outrage",      "Dragon",   90,  100, 15, "physical"),
    202: MoveData(202, "Giga Drain",   "Grass",    60,  100, 10, "special"),
    210: MoveData(210, "Fury Cutter",  "Bug",      10,  95,  20, "physical"),
    214: MoveData(214, "Sleep Talk",   "Normal",   None,None, 10, "status"),
    216: MoveData(216, "Return",       "Normal",   None,100, 20, "physical"),
    231: MoveData(231, "Iron Tail",    "Steel",    100, 75,  15, "physical"),
    237: MoveData(237, "Hidden Power", "Normal",   None,100, 15, "special"),
    239: MoveData(239, "Twister",      "Dragon",   40,  100, 20, "special"),
    241: MoveData(241, "Sunny Day",    "Fire",     None,None, 5,  "status"),
    247: MoveData(247, "Shadow Ball",  "Ghost",    80,  100, 15, "special"),
    249: MoveData(249, "Rock Smash",   "Fighting", 20,  100, 15, "physical"),
    252: MoveData(252, "Fake Out",     "Normal",   40,  100, 10, "physical", priority=1),
    263: MoveData(263, "Facade",       "Normal",   70,  100, 20, "physical"),
    280: MoveData(280, "Brick Break",  "Fighting", 75,  100, 15, "physical"),
    290: MoveData(290, "Secret Power", "Normal",   70,  100, 20, "physical"),
    299: MoveData(299, "Blaze Kick",   "Fire",     85,  90,  10, "physical"),
    304: MoveData(304, "Hyper Voice",  "Normal",   90,  100, 10, "special"),
    314: MoveData(314, "Air Cutter",   "Flying",   55,  95,  25, "special"),
    318: MoveData(318, "Silver Wind",  "Bug",      60,  100, 5,  "special"),
    332: MoveData(332, "Aerial Ace",   "Flying",   60,  None, 20, "physical"),
    337: MoveData(337, "Dragon Claw",  "Dragon",   80,  100, 15, "physical"),
    338: MoveData(338, "Frenzy Plant", "Grass",    150, 90,  5,  "special"),
    339: MoveData(339, "Bulk Up",      "Fighting", None,None, 20, "status"),
    347: MoveData(347, "Calm Mind",    "Psychic",  None,None, 20, "status"),
    348: MoveData(348, "Leaf Blade",   "Grass",    70,  100, 15, "physical"),
    354: MoveData(354, "Overheat",     "Fire",     140, 90,  5,  "special"),
}


@lru_cache(maxsize=1)
def _load_moves_json() -> dict[int, MoveData]:
    """Load moves from data/moves.json if it exists."""
    path = DATA_DIR / "moves.json"
    if not path.exists():
        return {}

    with open(path) as f:
        raw = json.load(f)

    moves = {}
    for entry in raw:
        m = MoveData(
            id=entry["id"],
            name=entry["name"],
            type=entry["type"],
            power=entry.get("power"),
            accuracy=entry.get("accuracy"),
            pp=entry["pp"],
            damage_class=entry["damage_class"],
            priority=entry.get("priority", 0),
        )
        moves[m.id] = m
    return moves


def get_move(move_id: int) -> MoveData | None:
    """Look up a move by ID. Checks JSON file first, then built-in table."""
    json_moves = _load_moves_json()
    if move_id in json_moves:
        return json_moves[move_id]
    return BUILTIN_MOVES.get(move_id)


def get_move_name(move_id: int) -> str:
    """Get the name of a move by ID, or 'Unknown' if not found."""
    move = get_move(move_id)
    return move.name if move else f"Move#{move_id}"
