import re

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.utils.date_utils import parse_brazilian_date


class SymplaScraper(BaseScraper):
    """Scraper for sympla.com.br music events."""

    platform_name = "sympla"
    BASE_URL = "https://www.sympla.com.br/eventos/musica"

    async def scrape(self) -> list[dict]:
        events = []
        try:
            html = await self.fetch_page(self.BASE_URL)
            events = self._parse_listing(html)
            self.logger.info(f"Sympla: found {len(events)} events")
        except Exception as e:
            self.logger.error(f"Sympla scraping failed: {e}")
        return events

    def _parse_listing(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        events = []

        cards = soup.select(
            "[class*='EventCard'], [class*='event-card'], "
            "[data-testid*='event'], .sympla-card, article"
        )
        for card in cards:
            try:
                raw = self._parse_card(card)
                if raw and raw.get("title"):
                    events.append(self.normalize_event(raw))
            except Exception as e:
                self.logger.warning(f"Failed to parse Sympla card: {e}")

        return events

    def _parse_card(self, card) -> dict | None:
        title_el = card.select_one(
            "[class*='title'], h2, h3, [class*='name']"
        )
        if not title_el:
            return None

        title = title_el.get_text(strip=True)
        if not title:
            return None

        date_el = card.select_one(
            "[class*='date'], time, [class*='when']"
        )
        event_date = None
        if date_el:
            date_text = date_el.get("datetime") or date_el.get_text(strip=True)
            try:
                event_date = parse_brazilian_date(date_text)
            except Exception:
                pass

        location_el = card.select_one(
            "[class*='location'], [class*='local'], [class*='venue'], [class*='address']"
        )
        venue_name = ""
        city = ""
        if location_el:
            loc_text = location_el.get_text(strip=True)
            if " - " in loc_text:
                parts = loc_text.rsplit(" - ", 1)
                venue_name = parts[0].strip()
                city = parts[1].strip()
            else:
                venue_name = loc_text

        link_el = card.select_one("a[href]")
        source_url = None
        if link_el:
            href = link_el.get("href", "")
            if href.startswith("/"):
                source_url = f"https://www.sympla.com.br{href}"
            elif href.startswith("http"):
                source_url = href

        price_el = card.select_one("[class*='price'], [class*='valor']")
        ticket_price_min = None
        if price_el:
            price_text = price_el.get_text(strip=True)
            numbers = re.findall(r"[\d]+[.,]?\d*", price_text.replace(".", "").replace(",", "."))
            if numbers:
                try:
                    ticket_price_min = float(numbers[0])
                except ValueError:
                    pass

        return {
            "title": title,
            "artist_name": title,
            "venue_name": venue_name,
            "city": city,
            "event_date": event_date,
            "source_url": source_url,
            "ticket_price_min": ticket_price_min,
        }
