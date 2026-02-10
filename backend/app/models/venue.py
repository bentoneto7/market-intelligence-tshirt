from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, index=True, nullable=False)
    state: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue_type: Mapped[str | None] = mapped_column(String, nullable=True)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="venue")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
