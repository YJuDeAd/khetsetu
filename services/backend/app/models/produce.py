import uuid
from datetime import date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import ProduceStatus


class Produce(Base):
    __tablename__ = "listings"
    __table_args__ = (
        sa.CheckConstraint("quantity >= 0", name="chk_produce_non_negative_quantity"),
        sa.CheckConstraint("price_per_unit > 0", name="chk_produce_positive_price"),
        sa.CheckConstraint(
            "shelf_life_days > 0", name="chk_produce_positive_shelf_life"
        ),
        sa.Index(
            "idx_listings_crop_status_price", "crop_name", "status", "price_per_unit"
        ),
        sa.Index(
            "idx_listings_state_district_status",
            "location_state",
            "location_district",
            "status",
        ),
        sa.Index(
            "idx_listings_attributes_gin",
            "attributes",
            postgresql_using="gin",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    crop_name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    crop_category: Mapped[str] = mapped_column(
        sa.String(50),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2),
        nullable=False,
    )
    unit: Mapped[str] = mapped_column(
        sa.String(20),
        nullable=False,
        default="kg",
    )
    price_per_unit: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2),
        nullable=False,
    )
    harvest_date: Mapped[date] = mapped_column(
        sa.Date,
        nullable=False,
    )
    shelf_life_days: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=7,
    )
    status: Mapped[ProduceStatus] = mapped_column(
        sa.Enum(ProduceStatus, name="produce_status_enum", native_enum=False),
        nullable=False,
        default=ProduceStatus.ACTIVE,
        index=True,
    )
    location_pincode: Mapped[str] = mapped_column(
        sa.String(10),
        nullable=False,
        index=True,
    )
    location_district: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    location_state: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    location_lat: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(9, 6),
        nullable=True,
    )
    location_lng: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(9, 6),
        nullable=True,
    )
    attributes: Mapped[dict] = mapped_column(
        sa.JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    seller = relationship("User", back_populates="listings")
    orders = relationship("Order", back_populates="listing")
