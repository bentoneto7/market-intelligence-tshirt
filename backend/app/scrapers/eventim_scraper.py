import re

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.utils.date_utils import parse_brazilian_date


class EventimScraper(BaseScraper):
    """Scraper for eventim.com.br"""

    platform_name = "eventim"
    BASE_URL = "https://www.eventim.com.br/city/brazil/list"

    async def scrape(self) -> list[dict]:
        events = []
        try:
            html = await self.fetch_page(self.BASE_URL)
            events = self._parse_listing(html)
            self.logger.info(f"Eventim: found {len(events)} events")
        except Exception as e:
            self.logger.error(f"Eventim scraping failed: {e}")
        return events

    def _parse_listing(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        events = []

        cards = soup.select(".eventListItem, .event-card, [data-event-id]")
        for card in cards:
            try:
                raw = self._parse_card(card)
                if raw and raw.get("title"):
                    events.append(self.normalize_event(raw))
            except Exception as e:
                self.logger.warning(f"Failed to parse Eventim card: {e}")

        return events

    def _parse_card(self, card) -> dict | None:
        title_el = card.select_one(
            ".eventListItem-title, .event-title, h3, h2"
        )
        if not title_el:
            return None

        title = title_el.get_text(strip=True)

        date_el = card.select_one(
            ".eventListItem-date, .event-date, time, .date"
        )
        event_date = None
        if date_el:
            date_text = date_el.get("datetime") or date_el.get_text(strip=True)
            try:
                event_date = parse_brazilian_date(date_text)
            except Exception:
                pass

        venue_el = card.select_one(
            ".eventListItem-venue, .event-venue, .venue, .location"
        )
        venue_name = venue_el.get_text(strip=True) if venue_el else ""

        city_el = card.select_one(".eventListItem-city, .event-city, .city")
        city = city_el.get_text(strip=True) if city_el else ""

        # If city is embedded in venue text like "Arena - São Paulo"
        if not city and " - " in venue_name:
            parts = venue_name.rsplit(" - ", 1)
            venue_name = parts[0].strip()
            city = parts[1].strip()

        link_el = card.select_one("a[href]")
        source_url = None
        if link_el:
            href = link_el.get("href", "")
            if href.startswith("/"):
                source_url = f"https://www.eventim.com.br{href}"
            elif href.startswith("http"):
                source_url = href

        external_id = card.get("data-event-id", "")

        status_el = card.select_one(".soldout, .sold-out, .esgotado")
        ticket_status = "sold_out" if status_el else "available"

        price_el = card.select_one(".price, .eventListItem-price")
        ticket_price_min = None
        if price_el:
            price_text = price_el.get_text(strip=True)
            numbers = re.findall(r"[\d.,]+", price_text.replace(".", "").replace(",", "."))
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
            "state": self._guess_state(city),
            "event_date": event_date,
            "source_url": source_url,
            "external_id": external_id,
            "ticket_status": ticket_status,
            "ticket_price_min": ticket_price_min,
        }

    def _guess_state(self, city: str) -> str | None:
        city_state_map = {
            "são paulo": "SP",
            "rio de janeiro": "RJ",
            "belo horizonte": "MG",
            "curitiba": "PR",
            "porto alegre": "RS",
            "brasília": "DF",
            "salvador": "BA",
            "recife": "PE",
            "fortaleza": "CE",
            "florianópolis": "SC",
            "goiânia": "GO",
            "belém": "PA",
            "manaus": "AM",
            "campinas": "SP",
            "uberlândia": "MG",
        }
        return city_state_map.get(city.lower().strip())
