from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.marketplace import (
    MarketplaceProductResponse,
    MarketplaceStatsResponse,
    PaginatedMarketplaceResponse,
    SalesProjectionResponse,
)
from app.schemas.marketplace import ScrapeTriggerRequest
from app.services.marketplace_scraping_service import MarketplaceScrapingService
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/products", response_model=PaginatedMarketplaceResponse)
def list_products(
    platform: str | None = None,
    related_artist: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_sold: int | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = MarketplaceService(db)
    return service.list_products(
        platform=platform,
        related_artist=related_artist,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_sold=min_sold,
        search=search,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=MarketplaceStatsResponse)
def get_marketplace_stats(db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.get_stats()


@router.get("/projection", response_model=SalesProjectionResponse)
def get_sales_projection(db: Session = Depends(get_db)):
    service = MarketplaceService(db)
    return service.get_sales_projection()


@router.get("/event-forecast")
def get_event_forecast(
    days: int = Query(90, ge=7, le=365),
    db: Session = Depends(get_db),
):
    service = MarketplaceService(db)
    return service.get_event_forecast(days_ahead=days)


@router.post("/scrape")
async def scrape_marketplace(
    request: ScrapeTriggerRequest | None = None,
    db: Session = Depends(get_db),
):
    service = MarketplaceScrapingService(db)
    result = await service.scrape_for_events(
        custom_terms=request.search_terms if request else None
    )
    return result
