"""FireRed story progression tracker.

Provides the LLM with a "current objective" so it doesn't wander aimlessly.
"""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"


@dataclass
class ProgressionStep:
    step: int
    name: str
    description: str
    objective: str
    completion_check: str


@lru_cache(maxsize=1)
def load_progression() -> list[ProgressionStep]:
    """Load the progression steps from data/progression.json."""
    with open(DATA_DIR / "progression.json") as f:
        raw = json.load(f)

    return [
        ProgressionStep(
            step=entry["step"],
            name=entry["name"],
            description=entry["description"],
            objective=entry["objective"],
            completion_check=entry["completion_check"],
        )
        for entry in raw
    ]


def get_current_step(badge_count: int) -> ProgressionStep:
    """Estimate the current progression step based on badge count.

    This is a simple heuristic — badges are the most reliable progress marker.
    """
    steps = load_progression()

    # Map badge count to approximate step
    badge_to_step = {
        0: 1,  # Pre-Brock
        1: 6,  # Post-Brock, heading to Cerulean
        2: 8,  # Post-Misty, heading to Vermilion
        3: 10, # Post-Surge, heading to Celadon
        4: 12, # Post-Erika, Pokemon Tower
        5: 14, # Post-Koga, heading to Saffron
        6: 15, # Post-Sabrina, heading to Cinnabar
        7: 16, # Post-Blaine, heading to Viridian
        8: 17, # All badges, Victory Road
    }

    step_num = badge_to_step.get(badge_count, 18)

    for step in steps:
        if step.step == step_num:
            return step

    return steps[-1]


def get_step_by_number(step_num: int) -> ProgressionStep | None:
    """Get a specific progression step."""
    for step in load_progression():
        if step.step == step_num:
            return step
    return None
