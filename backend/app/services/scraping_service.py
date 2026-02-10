import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.analysis.genre_classifier import classify_genre
from app.analysis.hype_calculator import HypeCalculator
from app.analysis.production_window import ProductionWindowCalculator
from app.analysis.sales_predictor import SalesPotentialCalculator
from app.models.artist import Artist
from app.models.event import Event
from app.models.event_snapshot import EventSnapshot
from app.models.marketplace_product import MarketplaceProduct
from app.models.scraping_log import ScrapingLog
from app.models.venue import Venue
from app.scrapers.eventbrite_scraper import EventbriteScraper
from app.scrapers.eventim_scraper import EventimScraper
from app.scrapers.shopee_scraper import ShopeeScraper
from app.scrapers.sympla_scraper import SymplaScraper
from app.utils.date_utils import normalize_artist_name
from app.utils.logger import setup_logger

logger = setup_logger("scraping_service")


# Event scrapers (for shows/concerts)
EVENT_SCRAPERS = {
    "eventbrite": EventbriteScraper,
    "sympla": SymplaScraper,
    "eventim": EventimScraper,
}

# Marketplace scrapers (for products/t-shirts)
MARKETPLACE_SCRAPERS = {
    "shopee": ShopeeScraper,
}


class ScrapingService:
    def __init__(self, db: Session):
        self.db = db
        self.hype_calc = HypeCalculator()
        self.sales_calc = SalesPotentialCalculator()
        self.production_calc = ProductionWindowCalculator()

    async def run_scraping(self, platforms: list[str] | None = None) -> dict:
        """Run scraping for events and/or marketplace products."""
        all_platforms = list(EVENT_SCRAPERS.keys()) + list(MARKETPLACE_SCRAPERS.keys())
        target_platforms = platforms or all_platforms
        total_found = 0
        total_new = 0
        results = []

        for platform in target_platforms:
            if platform in EVENT_SCRAPERS:
                result = await self._scrape_events(platform)
            elif platform in MARKETPLACE_SCRAPERS:
                result = await self._scrape_marketplace(platform)
            else:
                logger.warning(f"Unknown platform: {platform}")
                results.append({"platform": platform, "status": "unknown"})
                continue

            results.append(result)
            total_found += result.get("found", 0)
            total_new += result.get("new", 0)

        return {
            "status": "completed",
            "message": f"Found {total_found} items, {total_new} new",
            "details": results,
        }

    async def _scrape_events(self, platform: str) -> dict:
        """Scrape events from a single platform."""
        scraper_cls = EVENT_SCRAPERS[platform]
        log = ScrapingLog(platform=platform, started_at=datetime.utcnow())
        start_time = time.time()

        try:
            scraper = scraper_cls()
            raw_events = await scraper.scrape()

            new_count = 0
            updated_count = 0

            for event_data in raw_events:
                if not event_data.get("event_date"):
                    continue
                created = self._process_event(event_data)
                if created:
                    new_count += 1
                else:
                    updated_count += 1

            self.db.commit()

            log.status = "success"
            log.events_found = len(raw_events)
            log.events_new = new_count
            log.events_updated = updated_count

            logger.info(
                f"Events [{platform}]: {len(raw_events)} found, "
                f"{new_count} new, {updated_count} updated"
            )

            result = {
                "platform": platform,
                "type": "events",
                "status": "success",
                "found": len(raw_events),
                "new": new_count,
                "updated": updated_count,
            }

        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            logger.error(f"Scraping events [{platform}] failed: {e}")
            self.db.rollback()
            result = {
                "platform": platform,
                "type": "events",
                "status": "failed",
                "error": str(e),
                "found": 0,
                "new": 0,
            }

        finally:
            log.duration_seconds = round(time.time() - start_time, 2)
            log.completed_at = datetime.utcnow()
            self.db.add(log)
            self.db.commit()

        return result

    async def _scrape_marketplace(self, platform: str) -> dict:
        """Scrape marketplace products from a platform."""
        scraper_cls = MARKETPLACE_SCRAPERS[platform]
        log = ScrapingLog(platform=f"{platform}_marketplace", started_at=datetime.utcnow())
        start_time = time.time()

        try:
            scraper = scraper_cls()
            products = await scraper.scrape()

            new_count = 0
            updated_count = 0

            for product_data in products:
                if not product_data.get("title") or product_data.get("price", 0) <= 0:
                    continue
                created = self._process_marketplace_product(product_data)
                if created:
                    new_count += 1
                else:
                    updated_count += 1

            self.db.commit()

            log.status = "success"
            log.events_found = len(products)
            log.events_new = new_count
            log.events_updated = updated_count

            logger.info(
                f"Marketplace [{platform}]: {len(products)} found, "
                f"{new_count} new, {updated_count} updated"
            )

            result = {
                "platform": platform,
                "type": "marketplace",
                "status": "success",
                "found": len(products),
                "new": new_count,
                "updated": updated_count,
            }

        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            logger.error(f"Scraping marketplace [{platform}] failed: {e}")
            self.db.rollback()
            result = {
                "platform": platform,
                "type": "marketplace",
                "status": "failed",
                "error": str(e),
                "found": 0,
                "new": 0,
            }

        finally:
            log.duration_seconds = round(time.time() - start_time, 2)
            log.completed_at = datetime.utcnow()
            self.db.add(log)
            self.db.commit()

        return result

    def _process_marketplace_product(self, data: dict) -> bool:
        """Process a single marketplace product. Returns True if new."""
        existing = None
        external_id = data.get("external_id")
        platform = data.get("platform", "shopee")

        if external_id:
            existing = (
                self.db.query(MarketplaceProduct)
                .filter(
                    MarketplaceProduct.external_id == external_id,
                    MarketplaceProduct.platform == platform,
                )
                .first()
            )

        if not existing:
            product_url = data.get("product_url", "")
            if product_url:
                existing = (
                    self.db.query(MarketplaceProduct)
                    .filter(MarketplaceProduct.product_url == product_url)
                    .first()
                )

        if existing:
            existing.price = data.get("price", existing.price)
            existing.sold_count = data.get("sold_count", existing.sold_count)
            existing.rating = data.get("rating", existing.rating)
            existing.review_count = data.get("review_count", existing.review_count)
            existing.original_price = data.get("original_price", existing.original_price)
            existing.last_scraped_at = datetime.utcnow()
            return False

        product = MarketplaceProduct(
            title=data["title"],
            product_url=data.get("product_url", ""),
            price=data.get("price", 0),
            original_price=data.get("original_price"),
            sold_count=data.get("sold_count", 0),
            rating=data.get("rating"),
            review_count=data.get("review_count", 0),
            seller_name=data.get("seller_name"),
            seller_location=data.get("seller_location"),
            platform=platform,
            category=data.get("category"),
            related_artist=data.get("related_artist"),
            search_term=data.get("search_term"),
            image_url=data.get("image_url"),
            external_id=data.get("external_id"),
        )
        self.db.add(product)
        return True

    def _process_event(self, data: dict) -> bool:
        """Process a single event dict. Returns True if new, False if updated."""
        source_url = data.get("source_url")

        existing = None
        if source_url:
            existing = (
                self.db.query(Event)
                .filter(Event.source_url == source_url)
                .first()
            )

        if existing:
            self._update_event(existing, data)
            self._maybe_create_snapshot(existing, data)
            self._recalculate_scores(existing)
            return False

        # Find or create artist
        artist = self._find_or_create_artist(
            data.get("artist_name", ""), data.get("title", "")
        )

        # Find or create venue
        venue = self._find_or_create_venue(
            data.get("venue_name", ""), data.get("city", ""), data.get("state")
        )

        event = Event(
            title=data["title"],
            artist_id=artist.id if artist else None,
            venue_id=venue.id if venue else None,
            event_date=data["event_date"],
            source_platform=data.get("source_platform"),
            source_url=source_url,
            external_id=data.get("external_id"),
            ticket_status=data.get("ticket_status", "available"),
            estimated_audience=data.get("estimated_audience"),
            ticket_price_min=data.get("ticket_price_min"),
            ticket_price_max=data.get("ticket_price_max"),
            event_type=data.get("event_type", "concert"),
            is_festival=data.get("is_festival", False),
            headliners=data.get("headliners"),
        )

        self.db.add(event)
        self.db.flush()

        # Create initial snapshot
        snapshot = EventSnapshot(
            event_id=event.id,
            ticket_status=event.ticket_status,
            estimated_audience=event.estimated_audience,
            ticket_price_min=event.ticket_price_min,
            ticket_price_max=event.ticket_price_max,
        )
        self.db.add(snapshot)

        self._recalculate_scores(event)
        return True

    def _find_or_create_artist(self, artist_name: str, title: str = "") -> Artist | None:
        if not artist_name:
            return None

        normalized = normalize_artist_name(artist_name)
        if not normalized:
            return None

        existing = (
            self.db.query(Artist)
            .filter(Artist.normalized_name == normalized)
            .first()
        )
        if existing:
            return existing

        genre = classify_genre(title, artist_name)
        artist = Artist(
            name=artist_name,
            normalized_name=normalized,
            genre=genre,
        )
        self.db.add(artist)
        self.db.flush()
        return artist

    def _find_or_create_venue(
        self, venue_name: str, city: str, state: str | None
    ) -> Venue | None:
        if not venue_name and not city:
            return None

        existing = (
            self.db.query(Venue)
            .filter(
                Venue.name == venue_name,
                Venue.city == city,
            )
            .first()
        )
        if existing:
            return existing

        venue = Venue(name=venue_name or "Unknown", city=city or "Unknown", state=state)
        self.db.add(venue)
        self.db.flush()
        return venue

    def _update_event(self, event: Event, data: dict):
        if data.get("ticket_status"):
            event.ticket_status = data["ticket_status"]
        if data.get("estimated_audience"):
            event.estimated_audience = data["estimated_audience"]
        if data.get("ticket_price_min"):
            event.ticket_price_min = data["ticket_price_min"]
        if data.get("ticket_price_max"):
            event.ticket_price_max = data["ticket_price_max"]
        event.last_scraped_at = datetime.utcnow()

    def _maybe_create_snapshot(self, event: Event, data: dict):
        last_snap = (
            self.db.query(EventSnapshot)
            .filter(EventSnapshot.event_id == event.id)
            .order_by(EventSnapshot.snapshot_at.desc())
            .first()
        )
        new_status = data.get("ticket_status")
        if last_snap and new_status and last_snap.ticket_status != new_status:
            snapshot = EventSnapshot(
                event_id=event.id,
                ticket_status=new_status,
                estimated_audience=data.get("estimated_audience"),
                ticket_price_min=data.get("ticket_price_min"),
                ticket_price_max=data.get("ticket_price_max"),
            )
            self.db.add(snapshot)

    def _recalculate_scores(self, event: Event):
        snapshots = (
            self.db.query(EventSnapshot)
            .filter(EventSnapshot.event_id == event.id)
            .order_by(EventSnapshot.snapshot_at.asc())
            .all()
        )

        hype = self.hype_calc.calculate(event, snapshots)
        event.hype_score = hype

        sales = self.sales_calc.calculate(event, hype)
        event.sales_potential_score = sales

        start, deadline = self.production_calc.calculate(event, hype, sales)
        event.production_start_date = start
        event.production_deadline = deadline

    def get_logs(self, platform: str | None = None, limit: int = 20) -> list[ScrapingLog]:
        query = self.db.query(ScrapingLog)
        if platform:
            query = query.filter(ScrapingLog.platform == platform)
        return (
            query.order_by(ScrapingLog.started_at.desc())
            .limit(limit)
            .all()
        )
