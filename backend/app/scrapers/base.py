import logging
from abc import ABC, abstractmethod

import httpx

from app.config import settings
from app.utils.rate_limiter import RateLimiter


class BaseScraper(ABC):
    """Abstract base class for all event scrapers."""

    platform_name: str = "unknown"

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rate_limiter = RateLimiter(
            calls_per_second=1.0 / settings.SCRAPING_RATE_LIMIT_SECONDS
        )
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def fetch_page(self, url: str) -> str:
        """Fetch a page with rate limiting and error handling."""
        await self.rate_limiter.acquire(self.platform_name)

        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=settings.SCRAPING_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    @abstractmethod
    async def scrape(self) -> list[dict]:
        """Main scraping method. Returns list of normalized event dicts."""
        ...

    def normalize_event(self, raw: dict) -> dict:
        """Ensure event dict has all expected keys."""
        return {
            "title": raw.get("title", ""),
            "artist_name": raw.get("artist_name", ""),
            "venue_name": raw.get("venue_name", ""),
            "city": raw.get("city", ""),
            "state": raw.get("state"),
            "event_date": raw.get("event_date"),
            "source_platform": self.platform_name,
            "source_url": raw.get("source_url"),
            "external_id": raw.get("external_id"),
            "ticket_status": raw.get("ticket_status", "available"),
            "estimated_audience": raw.get("estimated_audience"),
            "ticket_price_min": raw.get("ticket_price_min"),
            "ticket_price_max": raw.get("ticket_price_max"),
            "event_type": raw.get("event_type", "concert"),
            "is_festival": raw.get("is_festival", False),
            "headliners": raw.get("headliners"),
        }
