import uuid
from datetime import date, datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class MandiPriceHistory(Base):
    __tablename__ = "mandi_price_history"
    __table_args__ = (
        sa.CheckConstraint("modal_price > 0", name="chk_mandi_positive_modal_price"),
        sa.UniqueConstraint(
            "crop_name", "mandi_name", "state", "price_date", name="uq_mandi_crop_date"
        ),
        sa.Index("idx_mandi_crop_date_desc", "crop_name", sa.text("price_date DESC")),
        sa.Index(
            "idx_mandi_crop_state_date",
            "crop_name",
            "state",
            sa.text("price_date DESC"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    crop_name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    mandi_name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    state: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
        index=True,
    )
    district: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    modal_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(10, 2),
        nullable=False,
    )
    min_price: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(10, 2),
        nullable=True,
    )
    max_price: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(10, 2),
        nullable=True,
    )
    arrival_quantity: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(10, 2),
        nullable=True,
    )
    price_date: Mapped[date] = mapped_column(
        sa.Date,
        nullable=False,
        index=True,
    )
    is_fallback: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
