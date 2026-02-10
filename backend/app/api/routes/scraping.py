from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import ScrapingLogResponse, ScrapingTriggerRequest, ScrapingTriggerResponse
from app.services.scraping_service import ScrapingService

router = APIRouter(prefix="/scraping", tags=["scraping"])


@router.post("/trigger", response_model=ScrapingTriggerResponse)
async def trigger_scraping(
    request: ScrapingTriggerRequest | None = None,
    db: Session = Depends(get_db),
):
    service = ScrapingService(db)
    result = await service.run_scraping(
        platforms=request.platforms if request else None
    )
    return result


@router.get("/logs", response_model=list[ScrapingLogResponse])
def get_scraping_logs(
    platform: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ScrapingService(db)
    return service.get_logs(platform=platform, limit=limit)
