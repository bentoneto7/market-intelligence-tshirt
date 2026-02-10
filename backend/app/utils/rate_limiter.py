import asyncio
import time
from collections import defaultdict


class RateLimiter:
    """Token bucket rate limiter for scrapers."""

    def __init__(self, calls_per_second: float = 0.5):
        self.min_interval = 1.0 / calls_per_second
        self.last_call: dict[str, float] = defaultdict(float)

    async def acquire(self, key: str = "default"):
        now = time.time()
        elapsed = now - self.last_call[key]
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        self.last_call[key] = time.time()
