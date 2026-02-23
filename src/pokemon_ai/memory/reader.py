"""Typed memory read helpers for common data patterns."""

import struct

from pokemon_ai.emulator.client import EmulatorClient


async def read_u8(client: EmulatorClient, address: int) -> int:
    return await client.read_byte(address)


async def read_u16(client: EmulatorClient, address: int) -> int:
    return await client.read_halfword(address)


async def read_u32(client: EmulatorClient, address: int) -> int:
    return await client.read_word(address)


async def read_pointer(client: EmulatorClient, address: int) -> int:
    """Read a 32-bit pointer value."""
    return await read_u32(client, address)


async def read_string(client: EmulatorClient, address: int, length: int) -> str:
    """Read a Gen III encoded string and decode it to ASCII.

    Gen III uses a custom character encoding where 0xFF is the terminator.
    """
    raw = await client.read_bytes(address, length)
    return decode_gen3_string(raw)


# Gen III character table (subset covering common chars)
GEN3_CHARSET = {
    0xBB: "A", 0xBC: "B", 0xBD: "C", 0xBE: "D", 0xBF: "E",
    0xC0: "F", 0xC1: "G", 0xC2: "H", 0xC3: "I", 0xC4: "J",
    0xC5: "K", 0xC6: "L", 0xC7: "M", 0xC8: "N", 0xC9: "O",
    0xCA: "P", 0xCB: "Q", 0xCC: "R", 0xCD: "S", 0xCE: "T",
    0xCF: "U", 0xD0: "V", 0xD1: "W", 0xD2: "X", 0xD3: "Y",
    0xD4: "Z",
    0xD5: "a", 0xD6: "b", 0xD7: "c", 0xD8: "d", 0xD9: "e",
    0xDA: "f", 0xDB: "g", 0xDC: "h", 0xDD: "i", 0xDE: "j",
    0xDF: "k", 0xE0: "l", 0xE1: "m", 0xE2: "n", 0xE3: "o",
    0xE4: "p", 0xE5: "q", 0xE6: "r", 0xE7: "s", 0xE8: "t",
    0xE9: "u", 0xEA: "v", 0xEB: "w", 0xEC: "x", 0xED: "y",
    0xEE: "z",
    0xA1: "0", 0xA2: "1", 0xA3: "2", 0xA4: "3", 0xA5: "4",
    0xA6: "5", 0xA7: "6", 0xA8: "7", 0xA9: "8", 0xAA: "9",
    0x00: " ",
    0xAB: "!", 0xAC: "?", 0xAD: ".", 0xAE: "-",
    0xFF: "",  # terminator
}


def decode_gen3_string(data: bytes) -> str:
    """Decode a Gen III encoded byte string."""
    result = []
    for byte in data:
        if byte == 0xFF:
            break
        result.append(GEN3_CHARSET.get(byte, "?"))
    return "".join(result)


def parse_struct(data: bytes, fmt: str) -> tuple:
    """Unpack bytes using a struct format string."""
    return struct.unpack_from(f"<{fmt}", data)
