from datetime import date, datetime

from pydantic import BaseModel


class ArtistResponse(BaseModel):
    id: int
    name: str
    genre: str | None = None
    popularity_score: float = 0.0

    class Config:
        from_attributes = True


class VenueResponse(BaseModel):
    id: int
    name: str
    city: str
    state: str | None = None
    capacity: int | None = None
    venue_type: str | None = None

    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: int
    title: str
    event_date: datetime
    artist: ArtistResponse | None = None
    venue: VenueResponse | None = None
    source_platform: str | None = None
    source_url: str | None = None
    ticket_status: str | None = None
    estimated_audience: int | None = None
    ticket_price_min: float | None = None
    ticket_price_max: float | None = None
    event_type: str | None = None
    is_festival: bool = False
    headliners: list | dict | None = None
    hype_score: float = 0.0
    sales_potential_score: float = 0.0
    production_start_date: date | None = None
    production_deadline: date | None = None
    is_active: bool = True

    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    first_seen_at: datetime | None = None
    last_scraped_at: datetime | None = None
    snapshots: list["SnapshotResponse"] = []


class SnapshotResponse(BaseModel):
    id: int
    ticket_status: str | None = None
    estimated_audience: int | None = None
    ticket_price_min: float | None = None
    ticket_price_max: float | None = None
    snapshot_at: datetime

    class Config:
        from_attributes = True


class PaginatedEventResponse(BaseModel):
    events: list[EventResponse]
    total: int
    page: int
    page_size: int


class RankingResponse(BaseModel):
    events: list[EventResponse]
    metric: str


class DashboardStatsResponse(BaseModel):
    total_events: int
    high_hype_count: int
    high_potential_count: int
    events_this_month: int
    events_next_month: int
    top_cities: list[dict]
    top_genres: list[dict]


class ScrapingTriggerRequest(BaseModel):
    platforms: list[str] | None = None


class ScrapingTriggerResponse(BaseModel):
    status: str
    message: str
    details: list[dict] | None = None


class ScrapingLogResponse(BaseModel):
    id: int
    platform: str
    status: str | None = None
    events_found: int = 0
    events_new: int = 0
    events_updated: int = 0
    error_message: str | None = None
    duration_seconds: float | None = None
    started_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
