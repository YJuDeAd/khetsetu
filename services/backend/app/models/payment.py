import uuid
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import EscrowStatus


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        sa.CheckConstraint("amount > 0", name="chk_payment_positive_amount"),
        sa.Index("idx_payments_order_escrow", "order_id", "escrow_status"),
        sa.Index("idx_payments_escrow_status", "escrow_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("orders.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        sa.String(3),
        default="INR",
        nullable=False,
    )
    payment_method: Mapped[str] = mapped_column(
        sa.String(50),
        default="UPI",
        nullable=False,
    )
    escrow_status: Mapped[EscrowStatus] = mapped_column(
        sa.Enum(EscrowStatus, name="escrow_status_enum", native_enum=False),
        default=EscrowStatus.PENDING,
        nullable=False,
        index=True,
    )
    gateway_transaction_id: Mapped[str | None] = mapped_column(
        sa.String(100),
        nullable=True,
        index=True,
    )
    gateway_payment_id: Mapped[str | None] = mapped_column(
        sa.String(100),
        nullable=True,
    )
    held_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    released_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    refunded_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    metadata_json: Mapped[dict] = mapped_column(
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

    # Relationship
    order = relationship("Order", back_populates="payment")
