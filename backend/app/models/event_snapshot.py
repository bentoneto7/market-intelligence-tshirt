from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EventSnapshot(Base):
    __tablename__ = "event_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.id"), index=True, nullable=False
    )

    ticket_status: Mapped[str | None] = mapped_column(String)
    estimated_audience: Mapped[int | None] = mapped_column(Integer)
    ticket_price_min: Mapped[float | None] = mapped_column(Float)
    ticket_price_max: Mapped[float | None] = mapped_column(Float)

    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True
    )

    event: Mapped["Event"] = relationship("Event", back_populates="snapshots")
