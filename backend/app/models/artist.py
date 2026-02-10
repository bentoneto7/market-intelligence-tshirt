from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    normalized_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    genre: Mapped[str | None] = mapped_column(String, nullable=True)
    popularity_score: Mapped[float] = mapped_column(Float, default=0.0)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="artist")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
