import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    phone_number: Mapped[str] = mapped_column(
        sa.String(15),
        unique=True,
        index=True,
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        sa.String(255),
        unique=True,
        index=True,
        nullable=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        sa.String(150),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, name="user_role_enum", native_enum=False),
        nullable=False,
        index=True,
    )
    preferred_language: Mapped[str] = mapped_column(
        sa.String(10),
        default="hi",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        nullable=False,
    )
    profile_data: Mapped[dict] = mapped_column(
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
    listings = relationship(
        "Produce", back_populates="seller", cascade="all, delete-orphan"
    )
    buyer_orders = relationship(
        "Order", back_populates="buyer", foreign_keys="Order.buyer_id"
    )
    seller_orders = relationship(
        "Order", back_populates="seller", foreign_keys="Order.seller_id"
    )
