"""Tests for rate limiter."""

import time

import pytest

from pokemon_ai.llm.rate_limiter import RateLimiter, get_rate_limiter


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_allows_first_request(self):
        limiter = RateLimiter(requests_per_minute=60)
        start = time.monotonic()
        await limiter.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 0.1  # should be near-instant

    @pytest.mark.asyncio
    async def test_tracks_requests(self):
        limiter = RateLimiter(requests_per_minute=60)
        await limiter.acquire()
        assert len(limiter._timestamps) == 1

    def test_get_known_provider(self):
        limiter = get_rate_limiter("gemini")
        assert limiter.requests_per_minute == 15

    def test_get_unknown_provider(self):
        limiter = get_rate_limiter("unknown")
        assert limiter.requests_per_minute == 30
