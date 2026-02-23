"""Async client for mGBA-http REST API.

API docs: https://github.com/nikouu/mGBA-http/blob/main/docs/ApiDocumentation.md

Button tap:     POST /mgba-http/button/tap?button=A
Memory read:    GET /core/read8?address=0x02000000
Screenshot:     POST /core/screenshot?path=/tmp/screenshot.png
"""

import asyncio
import tempfile
from pathlib import Path

import httpx

from pokemon_ai.config import settings
from pokemon_ai.emulator.buttons import Button

# mGBA-http button names (capitalized first letter)
_BUTTON_NAMES = {
    Button.A: "A",
    Button.B: "B",
    Button.SELECT: "Select",
    Button.START: "Start",
    Button.RIGHT: "Right",
    Button.LEFT: "Left",
    Button.UP: "Up",
    Button.DOWN: "Down",
    Button.R: "R",
    Button.L: "L",
}


class EmulatorClient:
    """Communicates with mGBA via the mGBA-http plugin."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.mgba_url
        self._client: httpx.AsyncClient | None = None
        self._screenshot_dir = Path(tempfile.mkdtemp(prefix="pokemon_ai_"))

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("EmulatorClient must be used as async context manager")
        return self._client

    async def press_button(self, button: Button, duration_frames: int = 4) -> None:
        """Press and release a button."""
        name = _BUTTON_NAMES[button]
        await self.client.post(
            "/mgba-http/button/tap",
            params={"button": name},
        )
        # Small delay to let the emulator process
        await asyncio.sleep(0.05 * duration_frames)

    async def press_sequence(self, buttons: list[Button], delay: float = 0.15) -> None:
        """Press a sequence of buttons with delays between them."""
        for button in buttons:
            await self.press_button(button)
            await asyncio.sleep(delay)

    def _hex_addr(self, address: int) -> str:
        """Format an address as hex string with 0x prefix for mGBA-http."""
        return f"0x{address:08X}"

    async def read_byte(self, address: int) -> int:
        """Read a single byte from memory."""
        resp = await self.client.get(
            "/core/read8",
            params={"address": self._hex_addr(address)},
        )
        resp.raise_for_status()
        return int(resp.text)

    async def read_halfword(self, address: int) -> int:
        """Read a 16-bit value from memory."""
        resp = await self.client.get(
            "/core/read16",
            params={"address": self._hex_addr(address)},
        )
        resp.raise_for_status()
        return int(resp.text)

    async def read_word(self, address: int) -> int:
        """Read a 32-bit value from memory."""
        resp = await self.client.get(
            "/core/read32",
            params={"address": self._hex_addr(address)},
        )
        resp.raise_for_status()
        return int(resp.text)

    async def read_bytes(self, address: int, size: int) -> bytes:
        """Read a block of bytes from memory."""
        resp = await self.client.get(
            "/core/readrange",
            params={"address": self._hex_addr(address), "length": size},
        )
        resp.raise_for_status()
        # Response is comma-separated hex values like "0x1A,0x2B,0x3C"
        hex_values = resp.text.split(",")
        return bytes(int(v.strip(), 16) for v in hex_values if v.strip())

    async def screenshot(self) -> bytes:
        """Capture a screenshot and return PNG bytes."""
        path = self._screenshot_dir / "screen.png"
        resp = await self.client.post(
            "/core/screenshot",
            params={"path": str(path)},
        )
        resp.raise_for_status()
        # Read the saved file
        await asyncio.sleep(0.1)  # small delay for file write
        return path.read_bytes()

    async def is_connected(self) -> bool:
        """Check if the emulator is responding."""
        try:
            # Try reading a known ROM header address as a connectivity check
            resp = await self.client.get(
                "/core/read8",
                params={"address": "0x00000000"},
            )
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
