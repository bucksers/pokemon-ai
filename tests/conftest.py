"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_personality() -> int:
    """A known personality value for testing decryption."""
    return 0x12345678


@pytest.fixture
def sample_ot_id() -> int:
    """A known OT ID for testing decryption."""
    return 0xABCD1234
