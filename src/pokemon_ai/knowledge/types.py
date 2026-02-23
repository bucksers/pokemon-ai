"""Type effectiveness lookups from the type chart."""

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


@lru_cache(maxsize=1)
def _load_type_chart() -> dict[str, dict[str, float]]:
    with open(DATA_DIR / "type_chart.json") as f:
        return json.load(f)


def effectiveness(attack_type: str, defend_type: str) -> float:
    """Get the effectiveness multiplier for an attack type vs a defending type.

    Returns 2.0 (super effective), 1.0 (neutral), 0.5 (not very effective),
    or 0.0 (immune).
    """
    chart = _load_type_chart()
    attack_type = attack_type.capitalize()
    defend_type = defend_type.capitalize()

    if attack_type not in chart:
        return 1.0

    return chart[attack_type].get(defend_type, 1.0)


def dual_effectiveness(attack_type: str, defend_types: list[str]) -> float:
    """Get combined effectiveness against a dual-typed Pokemon."""
    result = 1.0
    for dt in defend_types:
        result *= effectiveness(attack_type, dt)
    return result


def get_weaknesses(pokemon_type: str) -> list[str]:
    """Get all types that are super effective against the given type."""
    chart = _load_type_chart()
    pokemon_type = pokemon_type.capitalize()
    weaknesses = []
    for atk_type, matchups in chart.items():
        if matchups.get(pokemon_type, 1.0) > 1.0:
            weaknesses.append(atk_type)
    return weaknesses


def get_resistances(pokemon_type: str) -> list[str]:
    """Get all types that are not very effective against the given type."""
    chart = _load_type_chart()
    pokemon_type = pokemon_type.capitalize()
    resistances = []
    for atk_type, matchups in chart.items():
        mult = matchups.get(pokemon_type, 1.0)
        if 0.0 < mult < 1.0:
            resistances.append(atk_type)
    return resistances


def get_immunities(pokemon_type: str) -> list[str]:
    """Get all types that have no effect against the given type."""
    chart = _load_type_chart()
    pokemon_type = pokemon_type.capitalize()
    immunities = []
    for atk_type, matchups in chart.items():
        if matchups.get(pokemon_type, 1.0) == 0.0:
            immunities.append(atk_type)
    return immunities


ALL_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug",
    "Rock", "Ghost", "Dragon", "Dark", "Steel",
]
