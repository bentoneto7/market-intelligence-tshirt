from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String, nullable=False)
    artist_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("artists.id"), index=True, nullable=True
    )
    venue_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("venues.id"), index=True, nullable=True
    )
    event_date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)

    source_platform: Mapped[str | None] = mapped_column(String, index=True)
    source_url: Mapped[str | None] = mapped_column(String, unique=True)
    external_id: Mapped[str | None] = mapped_column(String)

    ticket_status: Mapped[str | None] = mapped_column(String)  # available, selling_fast, sold_out
    estimated_audience: Mapped[int | None] = mapped_column(Integer)
    ticket_price_min: Mapped[float | None] = mapped_column(Float)
    ticket_price_max: Mapped[float | None] = mapped_column(Float)

    event_type: Mapped[str | None] = mapped_column(String)  # festival, concert, tour_stop
    is_festival: Mapped[bool] = mapped_column(Boolean, default=False)
    headliners: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    hype_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    sales_potential_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    production_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    production_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    artist: Mapped["Artist | None"] = relationship("Artist", back_populates="events")
    venue: Mapped["Venue | None"] = relationship("Venue", back_populates="events")
    snapshots: Mapped[list["EventSnapshot"]] = relationship(
        "EventSnapshot", back_populates="event"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
