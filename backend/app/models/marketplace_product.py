from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MarketplaceProduct(Base):
    __tablename__ = "marketplace_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Product info
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    product_url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # Pricing
    price: Mapped[float] = mapped_column(Float, nullable=False)
    original_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Sales metrics
    sold_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    # Seller info
    seller_name: Mapped[str | None] = mapped_column(String, nullable=True)
    seller_location: Mapped[str | None] = mapped_column(String, nullable=True)

    # Classification
    platform: Mapped[str] = mapped_column(String, index=True, nullable=False)  # shopee, mercadolivre
    category: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    related_artist: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    related_event: Mapped[str | None] = mapped_column(String, nullable=True)
    search_term: Mapped[str | None] = mapped_column(String, nullable=True)

    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
