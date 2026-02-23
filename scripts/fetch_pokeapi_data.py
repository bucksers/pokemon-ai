"""Fetch Pokemon and move data from PokeAPI and save to data/ directory.

Usage: uv run python scripts/fetch_pokeapi_data.py
"""

import asyncio
import json
from pathlib import Path

import httpx

DATA_DIR = Path(__file__).parent.parent / "data"
POKEAPI_BASE = "https://pokeapi.co/api/v2"

# Fetch Gen I-III Pokemon (1-386) — covers everything in FireRed
MAX_POKEMON = 386
MAX_MOVES = 354  # Gen III max move ID


async def fetch_pokemon(client: httpx.AsyncClient, pokemon_id: int) -> dict | None:
    try:
        resp = await client.get(f"{POKEAPI_BASE}/pokemon/{pokemon_id}")
        if resp.status_code != 200:
            return None
        data = resp.json()
        return {
            "id": data["id"],
            "name": data["name"].capitalize(),
            "types": [t["type"]["name"].capitalize() for t in data["types"]],
            "base_stats": {
                "hp": data["stats"][0]["base_stat"],
                "attack": data["stats"][1]["base_stat"],
                "defense": data["stats"][2]["base_stat"],
                "sp_atk": data["stats"][3]["base_stat"],
                "sp_def": data["stats"][4]["base_stat"],
                "speed": data["stats"][5]["base_stat"],
            },
        }
    except Exception as e:
        print(f"  Error fetching Pokemon #{pokemon_id}: {e}")
        return None


async def fetch_move(client: httpx.AsyncClient, move_id: int) -> dict | None:
    try:
        resp = await client.get(f"{POKEAPI_BASE}/move/{move_id}")
        if resp.status_code != 200:
            return None
        data = resp.json()
        return {
            "id": data["id"],
            "name": data["name"].replace("-", " ").title(),
            "type": data["type"]["name"].capitalize(),
            "power": data["power"],
            "accuracy": data["accuracy"],
            "pp": data["pp"],
            "damage_class": data["damage_class"]["name"],
            "priority": data["priority"],
        }
    except Exception as e:
        print(f"  Error fetching move #{move_id}: {e}")
        return None


async def main():
    DATA_DIR.mkdir(exist_ok=True)
    limits = httpx.Limits(max_connections=10)
    async with httpx.AsyncClient(timeout=30.0, limits=limits) as client:
        # Fetch Pokemon
        print(f"Fetching Pokemon 1-{MAX_POKEMON}...")
        pokemon = []
        batch_size = 20
        for start in range(1, MAX_POKEMON + 1, batch_size):
            end = min(start + batch_size, MAX_POKEMON + 1)
            batch = await asyncio.gather(
                *[fetch_pokemon(client, i) for i in range(start, end)]
            )
            pokemon.extend([p for p in batch if p])
            print(f"  {len(pokemon)} Pokemon fetched...")

        with open(DATA_DIR / "pokemon.json", "w") as f:
            json.dump(pokemon, f, indent=2)
        print(f"Saved {len(pokemon)} Pokemon to data/pokemon.json")

        # Fetch moves
        print(f"\nFetching moves 1-{MAX_MOVES}...")
        moves = []
        for start in range(1, MAX_MOVES + 1, batch_size):
            end = min(start + batch_size, MAX_MOVES + 1)
            batch = await asyncio.gather(
                *[fetch_move(client, i) for i in range(start, end)]
            )
            moves.extend([m for m in batch if m])
            print(f"  {len(moves)} moves fetched...")

        with open(DATA_DIR / "moves.json", "w") as f:
            json.dump(moves, f, indent=2)
        print(f"Saved {len(moves)} moves to data/moves.json")


if __name__ == "__main__":
    asyncio.run(main())
