"""Tests for Gen III Pokemon data decryption."""

import struct

import pytest

from pokemon_ai.memory.decrypt import (
    SUBSTRUCTURE_ORDER,
    decrypt_data_block,
    decrypt_pokemon,
    extract_ivs,
    get_substructure_positions,
    parse_attacks,
    parse_growth,
)


class TestDecryptDataBlock:
    def test_decryption_reverses_encryption(self):
        """Decrypting an encrypted block should give back the original data."""
        personality = 0x12345678
        ot_id = 0xABCD1234
        key = personality ^ ot_id

        # Create known plaintext
        plaintext = bytes(range(48))

        # Encrypt it
        encrypted = bytearray(48)
        for i in range(0, 48, 4):
            word = struct.unpack_from("<I", plaintext, i)[0]
            word ^= key
            struct.pack_into("<I", encrypted, i, word)

        # Decrypt should give back plaintext
        result = decrypt_data_block(bytes(encrypted), personality, ot_id)
        assert result == plaintext

    def test_zero_key_is_identity(self):
        """When personality XOR ot_id is 0, data is unchanged."""
        personality = 0x11111111
        ot_id = 0x11111111  # XOR = 0

        data = bytes(range(48))
        result = decrypt_data_block(data, personality, ot_id)
        assert result == data

    def test_block_length(self):
        """Decrypted block should always be 48 bytes."""
        result = decrypt_data_block(bytes(48), 0, 0)
        assert len(result) == 48


class TestSubstructureOrder:
    def test_all_24_orderings_exist(self):
        assert len(SUBSTRUCTURE_ORDER) == 24

    def test_each_ordering_has_all_four_letters(self):
        for order in SUBSTRUCTURE_ORDER:
            assert sorted(order) == ["A", "E", "G", "M"]

    def test_positions_cover_all_offsets(self):
        """Each substructure should be at offset 0, 12, 24, or 36."""
        for i in range(24):
            positions = get_substructure_positions(i)
            assert set(positions.values()) == {0, 12, 24, 36}


class TestParseGrowth:
    def test_parse_growth_basic(self):
        # species=25 (Pikachu), item=0, exp=1000, pp_bonuses=0, friendship=70
        data = struct.pack("<HHIBBxx", 25, 0, 1000, 0, 70)
        growth = parse_growth(data)
        assert growth.species == 25
        assert growth.item == 0
        assert growth.experience == 1000
        assert growth.friendship == 70


class TestParseAttacks:
    def test_parse_attacks_basic(self):
        # 4 moves with PP
        data = struct.pack("<HHHHBBBB", 84, 98, 45, 85, 30, 20, 25, 15)
        attacks = parse_attacks(data)
        assert attacks.move1 == 84
        assert attacks.move2 == 98
        assert attacks.move3 == 45
        assert attacks.move4 == 85
        assert attacks.pp1 == 30
        assert attacks.pp4 == 15


class TestExtractIVs:
    def test_all_zero_ivs(self):
        ivs = extract_ivs(0)
        assert all(v == 0 for v in ivs.values())

    def test_all_max_ivs(self):
        # All 31s = 0x3FFFFFFF (lower 30 bits all 1)
        ivs = extract_ivs(0x3FFFFFFF)
        assert all(v == 31 for v in ivs.values())

    def test_specific_ivs(self):
        # HP=15 (01111), Atk=20 (10100), rest 0
        val = 15 | (20 << 5)
        ivs = extract_ivs(val)
        assert ivs["hp"] == 15
        assert ivs["attack"] == 20
        assert ivs["defense"] == 0


class TestDecryptPokemon:
    def test_round_trip(self, sample_personality, sample_ot_id):
        """Create known data, encrypt it, then decrypt and verify."""
        key = sample_personality ^ sample_ot_id
        positions = get_substructure_positions(sample_personality)

        # Build plaintext with known Growth data
        plaintext = bytearray(48)
        g_offset = positions["G"]
        struct.pack_into("<HHIBBxx", plaintext, g_offset, 6, 0, 5000, 0, 70)  # Charizard

        # Build known Attacks data
        a_offset = positions["A"]
        struct.pack_into("<HHHHBBBB", plaintext, a_offset, 53, 7, 126, 14, 15, 25, 5, 20)

        # Encrypt
        encrypted = bytearray(48)
        for i in range(0, 48, 4):
            word = struct.unpack_from("<I", plaintext, i)[0]
            word ^= key
            struct.pack_into("<I", encrypted, i, word)

        growth, attacks, evs, misc = decrypt_pokemon(
            bytes(encrypted), sample_personality, sample_ot_id
        )

        assert growth.species == 6  # Charizard
        assert growth.experience == 5000
        assert attacks.move1 == 53
        assert attacks.move2 == 7
