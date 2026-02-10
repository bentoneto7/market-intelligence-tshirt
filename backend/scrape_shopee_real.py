"""
Scrape real Shopee products using their internal API.
Searches for t-shirts related to upcoming events and saves to database.
"""

import asyncio
import time
from datetime import datetime
from urllib.parse import quote

import httpx

from app.config import settings
from app.database import SessionLocal, init_db
from app.models.artist import Artist
from app.models.event import Event
from app.models.marketplace_product import MarketplaceProduct

SHOPEE_API_URL = "https://shopee.com.br/api/v4/search/search_items"

HEADERS = {
    "User-Agent": settings.USER_AGENT,
    "Accept": "application/json",
    "Referer": "https://shopee.com.br/",
    "X-Requested-With": "XMLHttpRequest",
    "af-ac-enc-dat": "",
}

SEARCH_TERMS = [
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


async def search_shopee(term: str, limit: int = 10) -> list[dict]:
    """Search Shopee API for products."""
    params = {
        "by": "sales",  # Sort by sales
        "keyword": term,
        "limit": limit,
        "newest": 0,
        "order": "desc",
        "page_type": "search",
        "scenario": "PAGE_GLOBAL_SEARCH",
        "version": 2,
    }

    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        try:
            resp = await client.get(SHOPEE_API_URL, params=params)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items") or []
                return items
            else:
                print(f"  Shopee API returned {resp.status_code} for '{term}'")
                return []
        except Exception as e:
            print(f"  Shopee API error for '{term}': {e}")
            return []


def parse_shopee_item(item: dict, search_term: str, artist: str | None) -> dict | None:
    """Parse a Shopee API item into our product format."""
    info = item.get("item_basic") or item
    if not info:
        return None

    name = info.get("name", "")
    if not name:
        return None

    item_id = info.get("itemid") or info.get("item_id", "")
    shop_id = info.get("shopid") or info.get("shop_id", "")

    # Build real product URL
    slug = name.lower().replace(" ", "-").replace("/", "-")[:80]
    product_url = f"https://shopee.com.br/{quote(slug)}-i.{shop_id}.{item_id}"

    # Price (Shopee returns in cents)
    price_raw = info.get("price", 0)
    price = price_raw / 100000 if price_raw > 10000 else price_raw / 100 if price_raw > 100 else price_raw

    price_before_discount = info.get("price_before_discount", 0)
    original_price = None
    if price_before_discount and price_before_discount > 0:
        original_price = price_before_discount / 100000 if price_before_discount > 10000 else price_before_discount / 100 if price_before_discount > 100 else price_before_discount
        if original_price <= price:
            original_price = None

    # Sold
    sold = info.get("sold", 0) or info.get("historical_sold", 0)

    # Rating
    rating_star = info.get("item_rating", {})
    rating = None
    if isinstance(rating_star, dict):
        rating = rating_star.get("rating_star")
        if rating and rating == 0:
            rating = None
    elif isinstance(rating_star, (int, float)) and rating_star > 0:
        rating = rating_star

    rating_count = 0
    if isinstance(info.get("item_rating"), dict):
        rating_count = sum(info["item_rating"].get("rating_count", [0, 0, 0, 0, 0]))

    # Image
    image = info.get("image", "")
    image_url = f"https://down-br.img.susercontent.com/file/{image}" if image else None

    # Shop info
    shop_name = info.get("shop_name") or ""
    shop_location = info.get("shop_location") or ""

    # Category
    category = "camiseta_artista" if artist else "camiseta_generica"
    name_lower = name.lower()
    if any(w in name_lower for w in ["festival", "lollapalooza", "rock in rio", "monsters"]):
        category = "camiseta_festival"
    elif any(w in name_lower for w in ["banda", "band"]):
        category = "camiseta_banda"

    return {
        "title": name,
        "product_url": product_url,
        "price": round(price, 2) if price > 0 else 0,
        "original_price": round(original_price, 2) if original_price else None,
        "sold_count": sold,
        "rating": round(rating, 1) if rating else None,
        "review_count": rating_count,
        "seller_name": shop_name,
        "seller_location": shop_location,
        "platform": "shopee",
        "category": category,
        "related_artist": artist,
        "search_term": search_term,
        "image_url": image_url,
        "external_id": str(item_id),
    }


async def main():
    init_db()
    db = SessionLocal()

    # Clear old products
    db.query(MarketplaceProduct).delete()
    db.commit()

    total_saved = 0
    seen_urls = set()

    for term, artist in SEARCH_TERMS:
        print(f"Searching: '{term}' (artist: {artist or 'generic'})...")

        items = await search_shopee(term, limit=15)
        new_in_batch = 0

        for item in items:
            product_data = parse_shopee_item(item, term, artist)
            if not product_data or not product_data["title"]:
                continue

            # Skip duplicates
            url = product_data["product_url"]
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Skip if price is 0 (failed to parse)
            if product_data["price"] <= 0:
                continue

            product = MarketplaceProduct(
                title=product_data["title"],
                product_url=product_data["product_url"],
                price=product_data["price"],
                original_price=product_data.get("original_price"),
                sold_count=product_data.get("sold_count", 0),
                rating=product_data.get("rating"),
                review_count=product_data.get("review_count", 0),
                seller_name=product_data.get("seller_name"),
                seller_location=product_data.get("seller_location"),
                platform="shopee",
                category=product_data.get("category"),
                related_artist=product_data.get("related_artist"),
                search_term=product_data.get("search_term"),
                image_url=product_data.get("image_url"),
                external_id=product_data.get("external_id"),
            )
            db.add(product)
            new_in_batch += 1

        if new_in_batch > 0:
            db.commit()
            total_saved += new_in_batch
            print(f"  -> Saved {new_in_batch} products")
        else:
            print(f"  -> No products found (Shopee may require browser rendering)")

        # Rate limit
        await asyncio.sleep(2)

    print(f"\nTotal: {total_saved} products saved to database")
    db.close()


if __name__ == "__main__":
    asyncio.run(main())
