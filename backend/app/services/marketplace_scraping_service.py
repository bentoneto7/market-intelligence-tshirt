"""Service to scrape marketplace products for artists related to upcoming events."""

import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.artist import Artist
from app.models.event import Event
from app.models.marketplace_product import MarketplaceProduct
from app.models.scraping_log import ScrapingLog
from app.scrapers.shopee_scraper import ShopeeScraper
from app.utils.logger import setup_logger

logger = setup_logger("marketplace_scraping")

# Default search terms per artist - what people search for on Shopee
DEFAULT_SEARCH_TEMPLATES = [
    "camiseta {artist}",
]


class MarketplaceScrapingService:
    def __init__(self, db: Session):
        self.db = db
        self.scraper = ShopeeScraper()

    async def scrape_for_events(self, custom_terms: list[str] | None = None) -> dict:
        """Scrape Shopee for t-shirts related to upcoming events."""
        search_terms = []

        if custom_terms:
            search_terms = [(term, None) for term in custom_terms]
        else:
            # Get distinct artists from upcoming events
            artists = (
                self.db.query(Artist)
                .join(Event, Event.artist_id == Artist.id)
                .filter(Event.is_active.is_(True))
                .filter(Event.event_date >= datetime.utcnow())
                .distinct()
                .all()
            )
            for artist in artists:
                for template in DEFAULT_SEARCH_TEMPLATES:
                    term = template.format(artist=artist.name)
                    search_terms.append((term, artist.name))

        total_found = 0
        total_new = 0

        log = ScrapingLog(
            platform="shopee_marketplace",
            started_at=datetime.utcnow(),
        )
        start_time = time.time()

        try:
            for term, artist_name in search_terms:
                products = await self.scraper.scrape_term(term, artist_name)
                for product_data in products:
                    created = self._save_product(product_data)
                    total_found += 1
                    if created:
                        total_new += 1

                self.db.commit()

            log.status = "success"
            log.events_found = total_found
            log.events_new = total_new
            log.events_updated = total_found - total_new

        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            logger.error(f"Marketplace scraping failed: {e}")
            self.db.rollback()

        finally:
            log.duration_seconds = round(time.time() - start_time, 2)
            log.completed_at = datetime.utcnow()
            self.db.add(log)
            self.db.commit()

        return {
            "status": "completed",
            "message": f"Found {total_found} products, {total_new} new",
        }

    def _save_product(self, data: dict) -> bool:
        """Save or update a product. Returns True if new."""
        url = data.get("product_url")
        if not url:
            return False

        existing = (
            self.db.query(MarketplaceProduct)
            .filter(MarketplaceProduct.product_url == url)
            .first()
        )

        if existing:
            # Update metrics
            if data.get("sold_count") and data["sold_count"] > 0:
                existing.sold_count = data["sold_count"]
            if data.get("price") and data["price"] > 0:
                existing.price = data["price"]
            if data.get("rating"):
                existing.rating = data["rating"]
            if data.get("image_url"):
                existing.image_url = data["image_url"]
            existing.last_scraped_at = datetime.utcnow()
            return False

        product = MarketplaceProduct(
            title=data.get("title", ""),
            product_url=url,
            price=data.get("price", 0),
            original_price=data.get("original_price"),
            sold_count=data.get("sold_count", 0),
            rating=data.get("rating"),
            review_count=data.get("review_count", 0),
            seller_name=data.get("seller_name"),
            seller_location=data.get("seller_location"),
            platform=data.get("platform", "shopee"),
            category=data.get("category"),
            related_artist=data.get("related_artist"),
            related_event=data.get("related_event"),
            search_term=data.get("search_term"),
            image_url=data.get("image_url"),
        )
        self.db.add(product)
        self.db.flush()
        return True
