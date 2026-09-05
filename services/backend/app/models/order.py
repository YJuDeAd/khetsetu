import uuid
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        sa.CheckConstraint("quantity > 0", name="chk_order_positive_quantity"),
        sa.CheckConstraint("unit_price > 0", name="chk_order_positive_unit_price"),
        sa.CheckConstraint("total_amount >= 0", name="chk_order_non_negative_total"),
        sa.CheckConstraint("platform_fee >= 0", name="chk_order_non_negative_fee"),
        sa.Index("idx_orders_buyer_status", "buyer_id", "status"),
        sa.Index("idx_orders_seller_status", "seller_id", "status"),
        sa.Index("idx_orders_status_created", "status", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("listings.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2),
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2),
        nullable=False,
    )
    platform_fee: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        sa.Enum(OrderStatus, name="order_status_enum", native_enum=False),
        default=OrderStatus.INITIATED,
        nullable=False,
        index=True,
    )
    delivery_address: Mapped[dict] = mapped_column(
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
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="buyer_orders")
    seller = relationship(
        "User", foreign_keys=[seller_id], back_populates="seller_orders"
    )
    listing = relationship("Produce", back_populates="orders")
    payment = relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )
