"""
Scraper for Shopee Brazil - searches for t-shirts related to events/artists.
Uses Shopee's internal search API with retry and fallback.
"""

import asyncio
import re
from urllib.parse import quote

import httpx

from app.scrapers.base import BaseScraper

SHOPEE_API_URL = "https://shopee.com.br/api/v4/search/search_items"

# Default search terms for t-shirt market intelligence
DEFAULT_SEARCH_TERMS = [
    ("camiseta ac dc", "AC/DC"),
    ("camiseta acdc rock", "AC/DC"),
    ("camiseta guns n roses", "Guns N' Roses"),
    ("camiseta guns roses", "Guns N' Roses"),
    ("camiseta my chemical romance", "My Chemical Romance"),
    ("camiseta mcr black parade", "My Chemical Romance"),
    ("camiseta bad bunny", "Bad Bunny"),
    ("camiseta the weeknd", "The Weeknd"),
    ("camiseta weeknd xo", "The Weeknd"),
    ("camiseta doja cat", "Doja Cat"),
    ("camiseta tyler the creator", "Tyler The Creator"),
    ("camiseta chappell roan", "Chappell Roan"),
    ("camiseta sabrina carpenter", "Sabrina Carpenter"),
    ("camiseta lollapalooza", None),
    ("camiseta lollapalooza 2026", None),
    ("camiseta monsters of rock", None),
    ("camiseta black label society", "Black Label Society"),
    ("camiseta cypress hill", "Cypress Hill"),
    ("camiseta interpol banda", "Interpol"),
    ("camiseta mac demarco", "Mac DeMarco"),
    ("camiseta bryan adams", "Bryan Adams"),
    ("camiseta jackson wang", "Jackson Wang"),
    ("camiseta banda rock", None),
    ("camiseta festival musica", None),
    ("camiseta rock vintage oversize", None),
]


class ShopeeScraper(BaseScraper):
    """Scraper for Shopee Brazil marketplace products."""

    platform_name = "shopee"
    BASE_URL = "https://shopee.com.br/search"
    MAX_RETRIES = 3

    def __init__(self):
        super().__init__()
        # Override headers for Shopee API
        self.api_headers = {
            "User-Agent": self.headers["User-Agent"],
            "Accept": "application/json",
            "Referer": "https://shopee.com.br/",
            "X-Requested-With": "XMLHttpRequest",
            "af-ac-enc-dat": "",
        }

    async def scrape(self) -> list[dict]:
        """Scrape all default search terms. Returns list of product dicts."""
        return await self.scrape_all_terms(DEFAULT_SEARCH_TERMS)

    async def scrape_all_terms(
        self, terms: list[tuple[str, str | None]] | None = None
    ) -> list[dict]:
        """Scrape multiple search terms with deduplication."""
        search_terms = terms or DEFAULT_SEARCH_TERMS
        all_products = []
        seen_urls = set()
        total_api_ok = 0
        total_api_blocked = 0

        for term, artist in search_terms:
            products = await self._search_with_retry(term, artist)

            for p in products:
                url = p.get("product_url", "")
                if url and url not in seen_urls and p.get("price", 0) > 0:
                    seen_urls.add(url)
                    all_products.append(p)

            if products:
                total_api_ok += 1
            else:
                total_api_blocked += 1

            await asyncio.sleep(2)  # Rate limit between searches

        self.logger.info(
            f"Shopee: {len(all_products)} products | "
            f"API ok: {total_api_ok}, blocked: {total_api_blocked}"
        )
        return all_products

    async def scrape_term(
        self, search_term: str, related_artist: str | None = None
    ) -> list[dict]:
        """Scrape a single search term."""
        return await self._search_with_retry(search_term, related_artist)

    async def _search_with_retry(
        self, term: str, artist: str | None, limit: int = 15
    ) -> list[dict]:
        """Search Shopee API with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                items = await self._call_api(term, limit)
                if items:
                    products = []
                    for item in items:
                        p = self._parse_api_item(item, term, artist)
                        if p and p.get("title"):
                            products.append(p)
                    self.logger.info(
                        f"Shopee [{term}]: {len(products)} products (attempt {attempt + 1})"
                    )
                    return products
                else:
                    self.logger.warning(
                        f"Shopee [{term}]: 0 items (attempt {attempt + 1})"
                    )
            except Exception as e:
                self.logger.warning(
                    f"Shopee [{term}]: error on attempt {attempt + 1}: {e}"
                )

            if attempt < self.MAX_RETRIES - 1:
                wait = (attempt + 1) * 3  # 3s, 6s, 9s
                await asyncio.sleep(wait)

        self.logger.error(f"Shopee [{term}]: all {self.MAX_RETRIES} attempts failed")
        return []

    async def _call_api(self, term: str, limit: int = 15) -> list[dict]:
        """Call Shopee internal search API."""
        params = {
            "by": "sales",
            "keyword": term,
            "limit": limit,
            "newest": 0,
            "order": "desc",
            "page_type": "search",
            "scenario": "PAGE_GLOBAL_SEARCH",
            "version": 2,
        }

        async with httpx.AsyncClient(
            headers=self.api_headers,
            timeout=15,
            follow_redirects=True,
        ) as client:
            resp = await client.get(SHOPEE_API_URL, params=params)

            if resp.status_code == 200:
                data = resp.json()
                return data.get("items") or []
            elif resp.status_code == 403:
                self.logger.warning(f"Shopee API returned 403 (anti-bot) for '{term}'")
                return []
            else:
                self.logger.warning(f"Shopee API returned {resp.status_code} for '{term}'")
                return []

    def _parse_api_item(
        self, item: dict, search_term: str, artist: str | None
    ) -> dict | None:
        """Parse a Shopee API response item into product dict."""
        info = item.get("item_basic") or item
        if not info:
            return None

        name = info.get("name", "")
        if not name:
            return None

        item_id = info.get("itemid") or info.get("item_id", "")
        shop_id = info.get("shopid") or info.get("shop_id", "")

        # Build product URL
        slug = name.lower().replace(" ", "-").replace("/", "-")[:80]
        product_url = f"https://shopee.com.br/{quote(slug)}-i.{shop_id}.{item_id}"

        # Price (Shopee returns in variable formats)
        price_raw = info.get("price", 0)
        if price_raw > 10000:
            price = price_raw / 100000
        elif price_raw > 100:
            price = price_raw / 100
        else:
            price = price_raw

        # Original price
        original_price = None
        price_before = info.get("price_before_discount", 0)
        if price_before and price_before > 0:
            if price_before > 10000:
                original_price = price_before / 100000
            elif price_before > 100:
                original_price = price_before / 100
            else:
                original_price = price_before
            if original_price <= price:
                original_price = None

        # Sold count
        sold = info.get("sold", 0) or info.get("historical_sold", 0)

        # Rating
        rating = None
        rating_data = info.get("item_rating", {})
        if isinstance(rating_data, dict):
            r = rating_data.get("rating_star")
            if r and r > 0:
                rating = r
        elif isinstance(rating_data, (int, float)) and rating_data > 0:
            rating = rating_data

        # Review count
        review_count = 0
        if isinstance(info.get("item_rating"), dict):
            counts = info["item_rating"].get("rating_count", [])
            if isinstance(counts, list):
                review_count = sum(counts)

        # Image
        image = info.get("image", "")
        image_url = f"https://down-br.img.susercontent.com/file/{image}" if image else None

        # Shop info
        shop_name = info.get("shop_name") or ""
        shop_location = info.get("shop_location") or ""

        # Category
        category = self._guess_category(name, artist)

        return {
            "title": name,
            "product_url": product_url,
            "price": round(price, 2) if price > 0 else 0,
            "original_price": round(original_price, 2) if original_price else None,
            "sold_count": sold,
            "rating": round(rating, 1) if rating else None,
            "review_count": review_count,
            "seller_name": shop_name,
            "seller_location": shop_location,
            "platform": "shopee",
            "category": category,
            "related_artist": artist,
            "search_term": search_term,
            "image_url": image_url,
            "external_id": str(item_id),
        }

    def _guess_category(self, title: str, related_artist: str | None) -> str:
        t = title.lower()
        if any(w in t for w in ["festival", "lollapalooza", "rock in rio", "monsters"]):
            return "camiseta_festival"
        if related_artist:
            return "camiseta_artista"
        if any(w in t for w in ["banda", "band", "rock", "metal", "punk"]):
            return "camiseta_banda"
        return "camiseta_generica"
