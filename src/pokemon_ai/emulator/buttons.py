"""GBA button definitions and common input sequences."""

from enum import IntEnum


class Button(IntEnum):
    """GBA button codes for mGBA-http."""
    A = 0
    B = 1
    SELECT = 2
    START = 3
    RIGHT = 4
    LEFT = 5
    UP = 6
    DOWN = 7
    R = 8
    L = 9


# Common button sequences for menu navigation
MENU_FIGHT = [Button.A]  # top-left in battle menu
MENU_BAG = [Button.RIGHT, Button.A]  # top-right
MENU_POKEMON = [Button.DOWN, Button.A]  # bottom-left
MENU_RUN = [Button.DOWN, Button.RIGHT, Button.A]  # bottom-right

# Move selection (1-4)
MOVE_SLOTS = {
    1: [Button.A],  # top-left
    2: [Button.RIGHT, Button.A],  # top-right
    3: [Button.DOWN, Button.A],  # bottom-left
    4: [Button.DOWN, Button.RIGHT, Button.A],  # bottom-right
}

# Dialogue advancement
ADVANCE_TEXT = [Button.A]
SKIP_TEXT = [Button.B]
