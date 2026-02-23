"""Action history ring buffer for tracking recent actions."""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ActionRecord:
    """A single action taken by the agent."""
    action: str  # e.g., "press_button A", "press_sequence UP A"
    reasoning: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class ActionHistory:
    """Ring buffer of recent actions for context and stuck detection."""

    def __init__(self, max_size: int = 50):
        self._buffer: deque[ActionRecord] = deque(maxlen=max_size)

    def add(self, action: str, reasoning: str | None = None) -> None:
        self._buffer.append(ActionRecord(action=action, reasoning=reasoning))

    @property
    def recent(self) -> list[ActionRecord]:
        return list(self._buffer)

    @property
    def last_n(self) -> list[str]:
        """Last 10 action strings for quick context."""
        return [r.action for r in list(self._buffer)[-10:]]

    def is_stuck(self, threshold: int = 8) -> bool:
        """Detect if the agent is repeating the same action."""
        recent = self.last_n
        if len(recent) < threshold:
            return False
        # Check if all recent actions are the same
        return len(set(recent[-threshold:])) <= 2

    def format_for_prompt(self) -> str:
        """Format recent history for LLM context."""
        if not self._buffer:
            return "No actions taken yet."
        lines = []
        for record in list(self._buffer)[-10:]:
            lines.append(f"- {record.action}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._buffer)
