from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.artist import Artist
from app.models.event import Event
from app.models.venue import Venue


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def list_events(
        self,
        city: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        min_hype: float | None = None,
        min_sales_potential: float | None = None,
        genre: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        query = (
            self.db.query(Event)
            .options(joinedload(Event.artist), joinedload(Event.venue))
            .filter(Event.is_active.is_(True))
        )

        if city:
            query = query.join(Venue).filter(Venue.city.ilike(f"%{city}%"))
        if date_from:
            query = query.filter(Event.event_date >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.filter(Event.event_date <= datetime.combine(date_to, datetime.max.time()))
        if min_hype is not None:
            query = query.filter(Event.hype_score >= min_hype)
        if min_sales_potential is not None:
            query = query.filter(Event.sales_potential_score >= min_sales_potential)
        if genre:
            if not city:
                query = query.join(Event.artist)
            else:
                query = query.join(Artist)
            query = query.filter(Artist.genre.ilike(f"%{genre}%"))

        total = query.count()
        events = (
            query.order_by(Event.event_date.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "events": events,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_event_detail(self, event_id: int) -> Event | None:
        return (
            self.db.query(Event)
            .options(
                joinedload(Event.artist),
                joinedload(Event.venue),
                joinedload(Event.snapshots),
            )
            .filter(Event.id == event_id)
            .first()
        )

    def get_rankings(self, metric: str = "sales_potential_score", limit: int = 20) -> list[Event]:
        order_col = (
            Event.sales_potential_score
            if metric == "sales_potential_score"
            else Event.hype_score
        )
        return (
            self.db.query(Event)
            .options(joinedload(Event.artist), joinedload(Event.venue))
            .filter(Event.is_active.is_(True))
            .filter(Event.event_date >= datetime.utcnow())
            .order_by(order_col.desc())
            .limit(limit)
            .all()
        )

    def get_dashboard_stats(self) -> dict:
        now = datetime.utcnow()
        base = self.db.query(Event).filter(
            Event.is_active.is_(True), Event.event_date >= now
        )

        total = base.count()
        high_hype = base.filter(Event.hype_score >= 70).count()
        high_potential = base.filter(Event.sales_potential_score >= 70).count()

        current_month_end = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        events_this_month = base.filter(Event.event_date < current_month_end).count()

        next_month_start = current_month_end
        next_month_end = datetime(
            next_month_start.year,
            next_month_start.month + 1 if next_month_start.month < 12 else 1,
            1,
            0, 0, 0,
        )
        if next_month_start.month == 12:
            next_month_end = datetime(next_month_start.year + 1, 1, 1)
        events_next_month = base.filter(
            Event.event_date >= next_month_start,
            Event.event_date < next_month_end,
        ).count()

        top_cities_rows = (
            self.db.query(Venue.city, func.count(Event.id).label("count"))
            .join(Event, Event.venue_id == Venue.id)
            .filter(Event.is_active.is_(True), Event.event_date >= now)
            .group_by(Venue.city)
            .order_by(func.count(Event.id).desc())
            .limit(5)
            .all()
        )
        top_cities = [{"city": row[0], "count": row[1]} for row in top_cities_rows]

        top_genres_rows = (
            self.db.query(Artist.genre, func.count(Event.id).label("count"))
            .join(Event, Event.artist_id == Artist.id)
            .filter(Event.is_active.is_(True), Event.event_date >= now, Artist.genre.isnot(None))
            .group_by(Artist.genre)
            .order_by(func.count(Event.id).desc())
            .limit(5)
            .all()
        )
        top_genres = [{"genre": row[0], "count": row[1]} for row in top_genres_rows]

        return {
            "total_events": total,
            "high_hype_count": high_hype,
            "high_potential_count": high_potential,
            "events_this_month": events_this_month,
            "events_next_month": events_next_month,
            "top_cities": top_cities,
            "top_genres": top_genres,
        }
