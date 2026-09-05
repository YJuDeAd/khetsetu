import uuid
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.enums import RouteStatus, StopStatus, StopType


class LogisticsHub(Base):
    __tablename__ = "logistics_hubs"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    hub_code: Mapped[str] = mapped_column(
        sa.String(20),
        unique=True,
        index=True,
        nullable=False,
    )
    pincode: Mapped[str] = mapped_column(
        sa.String(10),
        nullable=False,
        index=True,
    )
    district: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        sa.String(100),
        nullable=False,
    )
    lat: Mapped[Decimal] = mapped_column(
        sa.Numeric(9, 6),
        nullable=False,
    )
    lng: Mapped[Decimal] = mapped_column(
        sa.Numeric(9, 6),
        nullable=False,
    )
    has_cold_storage: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        nullable=False,
    )
    capacity_metric_tons: Mapped[Decimal] = mapped_column(
        sa.Numeric(10, 2),
        default=Decimal("50.00"),
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


class DeliveryRoute(Base):
    __tablename__ = "delivery_routes"
    __table_args__ = (
        sa.CheckConstraint("total_capacity_kg > 0", name="chk_route_positive_capacity"),
        sa.CheckConstraint("current_load_kg >= 0", name="chk_route_non_negative_load"),
        sa.CheckConstraint(
            "current_load_kg <= total_capacity_kg",
            name="chk_route_load_within_capacity",
        ),
        sa.Index("idx_routes_status_cold", "status", "is_cold_chain"),
        sa.Index("idx_routes_driver_status", "driver_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    origin_hub_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("logistics_hubs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    destination_hub_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("logistics_hubs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[RouteStatus] = mapped_column(
        sa.Enum(RouteStatus, name="route_status_enum", native_enum=False),
        default=RouteStatus.PLANNED,
        nullable=False,
        index=True,
    )
    vehicle_type: Mapped[str] = mapped_column(
        sa.String(50),
        default="PICKUP_TRUCK",
        nullable=False,
    )
    total_capacity_kg: Mapped[Decimal] = mapped_column(
        sa.Numeric(10, 2),
        nullable=False,
    )
    current_load_kg: Mapped[Decimal] = mapped_column(
        sa.Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )
    is_cold_chain: Mapped[bool] = mapped_column(
        sa.Boolean,
        default=False,
        nullable=False,
    )
    optimization_metrics: Mapped[dict] = mapped_column(
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
    stops = relationship(
        "RouteStop",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="RouteStop.stop_number",
    )


class RouteStop(Base):
    __tablename__ = "route_stops"
    __table_args__ = (
        sa.UniqueConstraint("route_id", "stop_number", name="uq_route_stop_number"),
        sa.Index("idx_stops_route_sequence", "route_id", "stop_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("delivery_routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    stop_number: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
    )
    stop_type: Mapped[StopType] = mapped_column(
        sa.Enum(StopType, name="stop_type_enum", native_enum=False),
        nullable=False,
    )
    status: Mapped[StopStatus] = mapped_column(
        sa.Enum(StopStatus, name="stop_status_enum", native_enum=False),
        default=StopStatus.PENDING,
        nullable=False,
    )
    eta: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    location_data: Mapped[dict] = mapped_column(
        sa.JSON().with_variant(JSONB, "postgresql"),
        default=dict,
        nullable=False,
    )

    # Relationship
    route = relationship("DeliveryRoute", back_populates="stops")
