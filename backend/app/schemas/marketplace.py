from datetime import datetime

from pydantic import BaseModel


class MarketplaceProductResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    image_url: str | None = None
    product_url: str
    price: float
    original_price: float | None = None
    sold_count: int = 0
    rating: float | None = None
    review_count: int = 0
    seller_name: str | None = None
    seller_location: str | None = None
    platform: str
    category: str | None = None
    related_artist: str | None = None
    related_event: str | None = None
    search_term: str | None = None
    last_scraped_at: datetime | None = None

    class Config:
        from_attributes = True


class PaginatedMarketplaceResponse(BaseModel):
    products: list[MarketplaceProductResponse]
    total: int
    page: int
    page_size: int


class MarketplaceStatsResponse(BaseModel):
    total_products: int
    avg_price: float
    top_sellers: list[dict]
    top_artists: list[dict]
    price_range: dict
    platform_breakdown: list[dict]


class MarketplaceFilters(BaseModel):
    platform: str | None = None
    related_artist: str | None = None
    category: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_sold: int | None = None
    search: str | None = None
    sort_by: str | None = None  # price, sold_count, rating
    page: int = 1
    page_size: int = 30


class ScrapeTriggerRequest(BaseModel):
    search_terms: list[str] | None = None
    platforms: list[str] | None = None


class ArtistProjection(BaseModel):
    artist: str
    total_sold: int
    avg_price: float
    products_count: int
    estimated_monthly_revenue: float
    estimated_units_per_month: int
    market_share_pct: float
    growth_potential: str  # "alto", "medio", "baixo"
    suggested_price: float
    profit_margin_pct: float


class SalesProjectionResponse(BaseModel):
    total_market_revenue: float
    total_units_sold: int
    avg_ticket: float
    projections: list[ArtistProjection]
    category_breakdown: list[dict]
    opportunity_score: dict
