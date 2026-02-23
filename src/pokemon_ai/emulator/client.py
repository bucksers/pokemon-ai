"""Async client for mGBA-http REST API."""

import asyncio

import httpx

from pokemon_ai.config import settings
from pokemon_ai.emulator.buttons import Button


class EmulatorClient:
    """Communicates with mGBA via the mGBA-http plugin."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.mgba_url
        self._client: httpx.AsyncClient | None = None

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
        """Press and release a button for the given number of frames."""
        # mGBA-http: POST /button/tap with key name
        await self.client.post(
            "/mgba-http/button/tap",
            json={"key": button.name.lower(), "duration": duration_frames},
        )
        # Small delay to let the emulator process
        await asyncio.sleep(0.05 * duration_frames)

    async def press_sequence(self, buttons: list[Button], delay: float = 0.15) -> None:
        """Press a sequence of buttons with delays between them."""
        for button in buttons:
            await self.press_button(button)
            await asyncio.sleep(delay)

    async def read_byte(self, address: int) -> int:
        """Read a single byte from memory."""
        resp = await self.client.get(f"/mgba-http/memory/read8", params={"address": address})
        resp.raise_for_status()
        return resp.json()["value"]

    async def read_halfword(self, address: int) -> int:
        """Read a 16-bit value from memory."""
        resp = await self.client.get(f"/mgba-http/memory/read16", params={"address": address})
        resp.raise_for_status()
        return resp.json()["value"]

    async def read_word(self, address: int) -> int:
        """Read a 32-bit value from memory."""
        resp = await self.client.get(f"/mgba-http/memory/read32", params={"address": address})
        resp.raise_for_status()
        return resp.json()["value"]

    async def read_bytes(self, address: int, size: int) -> bytes:
        """Read a block of bytes from memory."""
        resp = await self.client.get(
            "/mgba-http/memory/readrange",
            params={"address": address, "size": size},
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        return bytes(data)

    async def screenshot(self) -> bytes:
        """Capture a screenshot as PNG bytes."""
        resp = await self.client.get("/mgba-http/screenshot")
        resp.raise_for_status()
        return resp.content

    async def is_connected(self) -> bool:
        """Check if the emulator is responding."""
        try:
            resp = await self.client.get("/mgba-http/status")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False
