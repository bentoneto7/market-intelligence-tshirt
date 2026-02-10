from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.event import EventDetailResponse, EventResponse, PaginatedEventResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=PaginatedEventResponse)
def list_events(
    city: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    min_hype: float | None = None,
    min_sales_potential: float | None = None,
    genre: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = EventService(db)
    result = service.list_events(
        city=city,
        date_from=date_from,
        date_to=date_to,
        min_hype=min_hype,
        min_sales_potential=min_sales_potential,
        genre=genre,
        page=page,
        page_size=page_size,
    )
    return result


@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    service = EventService(db)
    event = service.get_event_detail(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
