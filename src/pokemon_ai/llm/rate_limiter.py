"""Per-provider rate limiting."""

import asyncio
import time
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    """Token bucket rate limiter for API calls."""

    requests_per_minute: float
    _timestamps: list[float] = field(default_factory=list)

    @property
    def min_interval(self) -> float:
        return 60.0 / self.requests_per_minute

    async def acquire(self) -> None:
        """Wait until a request is allowed."""
        now = time.monotonic()

        # Remove timestamps older than 1 minute
        cutoff = now - 60.0
        self._timestamps = [t for t in self._timestamps if t > cutoff]

        if len(self._timestamps) >= self.requests_per_minute:
            # Wait until the oldest request expires
            wait_time = self._timestamps[0] - cutoff
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self._timestamps.append(time.monotonic())


# Default rate limiters per provider
RATE_LIMITS = {
    "ollama": RateLimiter(requests_per_minute=60),  # local, no real limit
    "gemini": RateLimiter(requests_per_minute=15),   # free tier: 15 RPM
    "claude": RateLimiter(requests_per_minute=50),   # tier 1
    "openai": RateLimiter(requests_per_minute=50),   # tier 1
}


def get_rate_limiter(provider: str) -> RateLimiter:
    return RATE_LIMITS.get(provider, RateLimiter(requests_per_minute=30))
