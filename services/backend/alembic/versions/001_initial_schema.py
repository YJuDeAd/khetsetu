"""Initial schema for users, listings, orders, payments, logistics, and mandi prices

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-09-05 16:55:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Users Table
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("phone_number", sa.String(15), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column(
            "preferred_language", sa.String(10), nullable=False, server_default="hi"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "is_verified", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "profile_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_users_phone_unique", "users", ["phone_number"], unique=True)
    op.create_index("idx_users_email_unique", "users", ["email"], unique=True)
    op.create_index("idx_users_role", "users", ["role"])

    # 2. Logistics Hubs Table
    op.create_table(
        "logistics_hubs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("hub_code", sa.String(20), nullable=False),
        sa.Column("pincode", sa.String(10), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("lat", sa.Numeric(9, 6), nullable=False),
        sa.Column("lng", sa.Numeric(9, 6), nullable=False),
        sa.Column(
            "has_cold_storage", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "capacity_metric_tons",
            sa.Numeric(10, 2),
            nullable=False,
            server_default="50.00",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "idx_hubs_hub_code_unique", "logistics_hubs", ["hub_code"], unique=True
    )
    op.create_index("idx_hubs_pincode", "logistics_hubs", ["pincode"])
    op.create_index("idx_hubs_state_district", "logistics_hubs", ["state", "district"])

    # 3. Produce Listings Table
    op.create_table(
        "listings",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "seller_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("crop_name", sa.String(100), nullable=False),
        sa.Column("crop_category", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False, server_default="kg"),
        sa.Column("price_per_unit", sa.Numeric(12, 2), nullable=False),
        sa.Column("harvest_date", sa.Date(), nullable=False),
        sa.Column("shelf_life_days", sa.Integer(), nullable=False, server_default="7"),
        sa.Column("status", sa.String(30), nullable=False, server_default="ACTIVE"),
        sa.Column("location_pincode", sa.String(10), nullable=False),
        sa.Column("location_district", sa.String(100), nullable=False),
        sa.Column("location_state", sa.String(100), nullable=False),
        sa.Column("location_lat", sa.Numeric(9, 6), nullable=True),
        sa.Column("location_lng", sa.Numeric(9, 6), nullable=True),
        sa.Column(
            "attributes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("quantity >= 0", name="chk_produce_non_negative_quantity"),
        sa.CheckConstraint("price_per_unit > 0", name="chk_produce_positive_price"),
        sa.CheckConstraint(
            "shelf_life_days > 0", name="chk_produce_positive_shelf_life"
        ),
    )
    op.create_index("idx_listings_seller_id", "listings", ["seller_id"])
    op.create_index(
        "idx_listings_crop_status_price",
        "listings",
        ["crop_name", "status", "price_per_unit"],
    )
    op.create_index(
        "idx_listings_state_district_status",
        "listings",
        ["location_state", "location_district", "status"],
    )
    op.create_index("idx_listings_pincode", "listings", ["location_pincode"])
    op.create_index(
        "idx_listings_attributes_gin",
        "listings",
        ["attributes"],
        postgresql_using="gin",
    )

    # 4. Orders Table
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "buyer_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "seller_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "listing_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "platform_fee", sa.Numeric(12, 2), nullable=False, server_default="0.00"
        ),
        sa.Column("status", sa.String(30), nullable=False, server_default="INITIATED"),
        sa.Column(
            "delivery_address",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("quantity > 0", name="chk_order_positive_quantity"),
        sa.CheckConstraint("unit_price > 0", name="chk_order_positive_unit_price"),
        sa.CheckConstraint("total_amount >= 0", name="chk_order_non_negative_total"),
        sa.CheckConstraint("platform_fee >= 0", name="chk_order_non_negative_fee"),
    )
    op.create_index("idx_orders_buyer_status", "orders", ["buyer_id", "status"])
    op.create_index("idx_orders_seller_status", "orders", ["seller_id", "status"])
    op.create_index("idx_orders_listing_id", "orders", ["listing_id"])
    op.create_index("idx_orders_status_created", "orders", ["status", "created_at"])

    # 5. Payments / Escrow Transactions Table
    op.create_table(
        "payments",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "order_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column(
            "payment_method", sa.String(50), nullable=False, server_default="UPI"
        ),
        sa.Column(
            "escrow_status", sa.String(30), nullable=False, server_default="PENDING"
        ),
        sa.Column("gateway_transaction_id", sa.String(100), nullable=True),
        sa.Column("gateway_payment_id", sa.String(100), nullable=True),
        sa.Column("held_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("amount > 0", name="chk_payment_positive_amount"),
    )
    op.create_index("idx_payments_order_unique", "payments", ["order_id"], unique=True)
    op.create_index(
        "idx_payments_order_escrow", "payments", ["order_id", "escrow_status"]
    )
    op.create_index("idx_payments_escrow_status", "payments", ["escrow_status"])
    op.create_index("idx_payments_gateway_txn", "payments", ["gateway_transaction_id"])

    # 6. Delivery Routes Table
    op.create_table(
        "delivery_routes",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "driver_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "origin_hub_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("logistics_hubs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "destination_hub_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("logistics_hubs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(30), nullable=False, server_default="PLANNED"),
        sa.Column(
            "vehicle_type", sa.String(50), nullable=False, server_default="PICKUP_TRUCK"
        ),
        sa.Column("total_capacity_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "current_load_kg", sa.Numeric(10, 2), nullable=False, server_default="0.00"
        ),
        sa.Column(
            "is_cold_chain", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "optimization_metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("total_capacity_kg > 0", name="chk_route_positive_capacity"),
        sa.CheckConstraint("current_load_kg >= 0", name="chk_route_non_negative_load"),
        sa.CheckConstraint(
            "current_load_kg <= total_capacity_kg",
            name="chk_route_load_within_capacity",
        ),
    )
    op.create_index(
        "idx_routes_status_cold", "delivery_routes", ["status", "is_cold_chain"]
    )
    op.create_index(
        "idx_routes_driver_status", "delivery_routes", ["driver_id", "status"]
    )

    # 7. Route Stops Table (Sequenced pickup/dropoff for pooled VRP)
    op.create_table(
        "route_stops",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "route_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("delivery_routes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "order_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("stop_number", sa.Integer(), nullable=False),
        sa.Column("stop_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("eta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "location_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.UniqueConstraint("route_id", "stop_number", name="uq_route_stop_number"),
    )
    op.create_index(
        "idx_stops_route_sequence", "route_stops", ["route_id", "stop_number"]
    )
    op.create_index("idx_stops_order_id", "route_stops", ["order_id"])

    # 8. Mandi Price History Table
    op.create_table(
        "mandi_price_history",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("crop_name", sa.String(100), nullable=False),
        sa.Column("mandi_name", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("modal_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("min_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("arrival_quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column(
            "is_fallback", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("modal_price > 0", name="chk_mandi_positive_modal_price"),
        sa.UniqueConstraint(
            "crop_name", "mandi_name", "state", "price_date", name="uq_mandi_crop_date"
        ),
    )
    op.create_index(
        "idx_mandi_crop_date_desc",
        "mandi_price_history",
        ["crop_name", sa.text("price_date DESC")],
    )
    op.create_index(
        "idx_mandi_crop_state_date",
        "mandi_price_history",
        ["crop_name", "state", sa.text("price_date DESC")],
    )


def downgrade() -> None:
    op.drop_table("mandi_price_history")
    op.drop_table("route_stops")
    op.drop_table("delivery_routes")
    op.drop_table("payments")
    op.drop_table("orders")
    op.drop_table("listings")
    op.drop_table("logistics_hubs")
    op.drop_table("users")
