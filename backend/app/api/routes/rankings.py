from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import RankingResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/", response_model=RankingResponse)
def get_rankings(
    metric: str = Query("sales_potential_score", pattern="^(sales_potential_score|hype_score)$"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = EventService(db)
    events = service.get_rankings(metric=metric, limit=limit)
    return {"events": events, "metric": metric}
