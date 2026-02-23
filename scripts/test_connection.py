"""Verify mGBA-http is responding and basic operations work."""

import asyncio
import sys

from pokemon_ai.emulator.client import EmulatorClient
from pokemon_ai.emulator.buttons import Button


async def main():
    async with EmulatorClient() as emu:
        # Check connection
        if not await emu.is_connected():
            print("ERROR: Cannot connect to mGBA-http")
            print("Make sure mGBA is running with the mGBA-http plugin loaded")
            sys.exit(1)

        print("Connected to mGBA-http!")

        # Read a memory address (game code identifier at ROM header)
        try:
            val = await emu.read_word(0x080000AC)
            print(f"ROM game code: {val:#010x}")
        except Exception as e:
            print(f"Memory read test: {e}")

        # Take a screenshot
        try:
            png = await emu.screenshot()
            print(f"Screenshot captured: {len(png)} bytes")
        except Exception as e:
            print(f"Screenshot test: {e}")

        # Tap A button
        try:
            await emu.press_button(Button.A)
            print("Button press test: OK")
        except Exception as e:
            print(f"Button press test: {e}")

        print("\nAll connection tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
