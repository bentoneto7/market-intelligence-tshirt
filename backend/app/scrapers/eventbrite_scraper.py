"""Scraper for Eventbrite Brazil - extracts music events from LD+JSON structured data."""

import json
import re
from datetime import datetime

from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper
from app.utils.date_utils import normalize_artist_name


class EventbriteScraper(BaseScraper):
    """Scraper for eventbrite.com.br using structured LD+JSON data."""

    platform_name = "eventbrite"

    # Search pages to scrape (music events in Brazil)
    SEARCH_URLS = [
        "https://www.eventbrite.com.br/d/brazil/shows-musicais/?page=1",
        "https://www.eventbrite.com.br/d/brazil/shows-musicais/?page=2",
        "https://www.eventbrite.com.br/d/brazil/concertos/?page=1",
        "https://www.eventbrite.com.br/d/brazil/festivais-de-musica/?page=1",
    ]

    # Known artists from our events database to match
    KNOWN_ARTISTS = [
        "ac/dc", "acdc", "guns n' roses", "guns n roses", "my chemical romance",
        "mcr", "bad bunny", "the weeknd", "weeknd", "doja cat", "tyler the creator",
        "chappell roan", "sabrina carpenter", "black label society", "cypress hill",
        "interpol", "mac demarco", "bryan adams", "jackson wang", "marisa monte",
        "lollapalooza", "monsters of rock", "rock in rio",
    ]

    # Brazilian state mapping
    CITY_STATE_MAP = {
        "são paulo": "SP", "sao paulo": "SP", "santo amaro": "SP", "campinas": "SP",
        "rio de janeiro": "RJ",
        "belo horizonte": "MG", "uberlândia": "MG",
        "curitiba": "PR",
        "porto alegre": "RS",
        "brasília": "DF", "brasilia": "DF",
        "salvador": "BA",
        "recife": "PE",
        "fortaleza": "CE",
        "florianópolis": "SC", "florianopolis": "SC",
        "goiânia": "GO", "goiania": "GO",
        "belém": "PA", "belem": "PA",
        "manaus": "AM",
        "campina grande": "PB",
        "natal": "RN",
        "vitória": "ES", "vitoria": "ES",
    }

    async def scrape(self) -> list[dict]:
        """Scrape all Eventbrite search pages for music events."""
        all_events = []
        seen_urls = set()

        for url in self.SEARCH_URLS:
            try:
                html = await self.fetch_page(url)
                events = self._parse_ld_json(html)
                for ev in events:
                    source_url = ev.get("source_url", "")
                    if source_url and source_url not in seen_urls:
                        seen_urls.add(source_url)
                        all_events.append(ev)
                self.logger.info(f"Eventbrite [{url.split('?')[0].split('/')[-2]}]: {len(events)} events")
            except Exception as e:
                self.logger.error(f"Eventbrite scraping failed for {url}: {e}")

        self.logger.info(f"Eventbrite total: {len(all_events)} unique events")
        return all_events

    def _parse_ld_json(self, html: str) -> list[dict]:
        """Extract events from LD+JSON structured data."""
        soup = BeautifulSoup(html, "lxml")
        events = []

        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict) and data.get("@type") == "ItemList":
                    for element in data.get("itemListElement", []):
                        item = element.get("item", element)
                        event = self._parse_event_item(item)
                        if event:
                            events.append(self.normalize_event(event))
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Failed to parse LD+JSON: {e}")

        return events

    def _parse_event_item(self, item: dict) -> dict | None:
        """Parse a single event from LD+JSON item."""
        name = item.get("name", "").strip()
        if not name:
            return None

        # Skip non-music events
        name_lower = name.lower()
        skip_words = [
            "workshop", "curso", "aula", "palestra", "congresso", "treinamento", "imersão",
            "scuba", "mergulho", "yoga", "meditação", "gastronomia", "culinária",
            "biohacking", "expo", "magia", "bruxaria", "startup", "hackathon",
            "conferência", "conference", "webinar", "masterclass", "bootcamp",
            "networking", "meetup", "yacht party", "boat party", "open bar",
            "degustação", "wine", "cerveja", "running", "corrida", "maratona",
            "futebol", "soccer", "basquete", "esporte", "teatro", "stand-up",
            "comédia", "comedy", "cosplay", "anime", "gaming",
        ]
        if any(w in name_lower for w in skip_words):
            return None

        # Music keywords boost (at least one should be present)
        music_words = [
            "show", "concert", "tour", "live", "festival", "banda", "band",
            "rock", "pop", "sertanejo", "funk", "mpb", "jazz", "blues",
            "hip hop", "rap", "eletrônica", "dj", "samba", "pagode", "forró",
            "axé", "reggae", "metal", "punk", "carnaval", "lollapalooza",
            "monsters", "excursão", "ao vivo", "música", "musica", "musical",
            "acústico", "acoustic", "unplugged", "rave", "festa", "baile",
        ]
        # Also check against known artists
        is_music = any(w in name_lower for w in music_words) or any(
            a in name_lower for a in self.KNOWN_ARTISTS
        )
        if not is_music:
            return None

        # Parse date
        start_date_str = item.get("startDate", "")
        event_date = None
        if start_date_str:
            try:
                event_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                try:
                    event_date = datetime.strptime(start_date_str[:10], "%Y-%m-%d")
                except Exception:
                    pass

        # Skip past events
        if event_date and event_date < datetime.now():
            return None

        # Location
        location = item.get("location", {})
        venue_name = ""
        city = ""
        state = None

        if isinstance(location, dict):
            venue_name = location.get("name", "")
            address = location.get("address", {})
            if isinstance(address, dict):
                city = address.get("addressLocality", "")
            elif isinstance(address, str):
                city = address
        elif isinstance(location, str):
            venue_name = location

        # Guess state from city
        if city:
            state = self._guess_state(city)

        # Source URL
        source_url = item.get("url", "")

        # Price
        ticket_price_min = None
        offers = item.get("offers", {})
        if isinstance(offers, dict):
            low_price = offers.get("lowPrice")
            if low_price:
                try:
                    ticket_price_min = float(low_price)
                except (ValueError, TypeError):
                    pass

        # Extract artist name from event title
        artist_name = self._extract_artist(name)

        # Detect if it's a festival
        is_festival = any(w in name_lower for w in [
            "festival", "lollapalooza", "rock in rio", "monsters of rock",
            "carnaval", "réveillon", "festa",
        ])

        # Detect ticket status
        ticket_status = "available"
        availability = ""
        if isinstance(offers, dict):
            availability = str(offers.get("availability", "")).lower()
        if "soldout" in availability or "esgotado" in name_lower:
            ticket_status = "sold_out"

        # Estimate audience based on event type
        estimated_audience = self._estimate_audience(name, is_festival, ticket_price_min)

        return {
            "title": name,
            "artist_name": artist_name or name,
            "venue_name": venue_name,
            "city": city,
            "state": state,
            "event_date": event_date,
            "source_url": source_url,
            "ticket_status": ticket_status,
            "ticket_price_min": ticket_price_min,
            "estimated_audience": estimated_audience,
            "is_festival": is_festival,
            "event_type": "festival" if is_festival else "concert",
        }

    def _estimate_audience(self, title: str, is_festival: bool, price: float | None) -> int:
        """Estimate audience size based on event characteristics."""
        title_lower = title.lower()

        # Large festivals
        if any(w in title_lower for w in ["lollapalooza", "rock in rio", "monsters of rock"]):
            return 60000

        # Carnaval events
        if "carnaval" in title_lower:
            return 30000

        # Known big artists
        big_artists = ["guns n roses", "ac/dc", "acdc", "bad bunny", "the weeknd", "my chemical romance"]
        if any(a in title_lower for a in big_artists):
            return 25000

        # Mid-tier artists
        mid_artists = ["doja cat", "tyler the creator", "sabrina carpenter", "chappell roan",
                        "marisa monte", "bryan adams"]
        if any(a in title_lower for a in mid_artists):
            return 12000

        # Generic festival
        if is_festival:
            return 15000

        # Excursion events (bus tours to shows)
        if "excursão" in title_lower or "excursao" in title_lower:
            return 5000  # The actual show audience, not the bus

        # Based on price (higher price = bigger venue usually)
        if price and price > 200:
            return 8000
        elif price and price > 100:
            return 5000

        # Default small/medium show
        return 3000

    def _extract_artist(self, title: str) -> str:
        """Try to extract artist name from event title."""
        title_lower = title.lower()

        # Check against known artists
        for artist in self.KNOWN_ARTISTS:
            if artist in title_lower:
                # Return properly capitalized version
                idx = title_lower.index(artist)
                return title[idx:idx + len(artist)].strip()

        # Common patterns: "Show Artista", "Artista em Cidade", "Excursão: Artista"
        patterns = [
            r"excurs[ãa]o[:\s]+(.+?)(?:\s+em\s+|\s+saindo|\s*$)",
            r"show\s+(?:d[aeo]s?\s+)?(.+?)(?:\s+em\s+|\s*-|\s*\||\s*$)",
            r"^(.+?)\s+(?:em|no|na|ao vivo|live)\s+",
        ]
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                artist = match.group(1).strip()
                # Don't return very long strings (probably not just an artist name)
                if len(artist) < 40:
                    return artist

        return ""

    def _guess_state(self, city: str) -> str | None:
        """Guess Brazilian state from city name."""
        city_key = city.lower().strip()
        return self.CITY_STATE_MAP.get(city_key)
