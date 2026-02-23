"""Debug script: print the current game state from the running emulator."""

import asyncio
import sys

from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.state.state_manager import StateManager


async def main():
    async with EmulatorClient() as emu:
        if not await emu.is_connected():
            print("ERROR: Cannot connect to mGBA-http")
            sys.exit(1)

        sm = StateManager(emu)
        state = await sm.get_state(include_screenshot=False)
        print(state.summary())

        # Print detailed party info
        if state.party:
            print("\n=== Detailed Party ===")
            for mon in state.party:
                print(f"\n{mon.nickname} (Species #{mon.species_id})")
                print(f"  Level: {mon.level}")
                print(f"  HP: {mon.current_hp}/{mon.max_hp} ({mon.hp_percent:.0f}%)")
                print(f"  Stats: ATK={mon.attack} DEF={mon.defense} "
                      f"SPD={mon.speed} SPA={mon.sp_atk} SPD={mon.sp_def}")
                print(f"  Moves: {mon.moves}")
                print(f"  PP: {mon.pp}")
                print(f"  Item: {mon.item}")
                print(f"  Status: {mon.status:#x}")

        if state.in_battle and state.battle_enemy:
            e = state.battle_enemy
            print(f"\n=== Enemy ===")
            print(f"Species #{e.species_id} Lv{e.level}")
            print(f"HP: {e.current_hp}/{e.max_hp}")
            print(f"Moves: {e.moves}")


if __name__ == "__main__":
    asyncio.run(main())
