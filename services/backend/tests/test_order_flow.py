from datetime import date
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Order,
    OrderStatus,
    Produce,
    ProduceStatus,
    User,
    UserRole,
)


@pytest.fixture
async def order_setup(db_session: AsyncSession):
    """Seed a farmer with a produce listing and a buyer for order flow tests."""
    farmer = User(
        phone_number="+919876543100",
        hashed_password="pw",
        full_name="Kisan Farmer",
        role=UserRole.FARMER,
    )
    buyer = User(
        phone_number="+919876543101",
        hashed_password="pw",
        full_name="Vyapari Buyer",
        role=UserRole.BUYER,
    )
    db_session.add_all([farmer, buyer])
    await db_session.flush()

    listing = Produce(
        seller_id=farmer.id,
        crop_name="Premium Basmati Rice",
        crop_category="Cereals",
        quantity=Decimal("1000.00"),
        unit="kg",
        price_per_unit=Decimal("60.00"),
        harvest_date=date.today(),
        shelf_life_days=365,
        status=ProduceStatus.ACTIVE,
        location_pincode="143001",
        location_district="Amritsar",
        location_state="Punjab",
    )
    db_session.add(listing)
    await db_session.flush()

    return {"farmer": farmer, "buyer": buyer, "listing": listing}


# ==============================================================================
# VALID ORDER FLOW TRANSITIONS (create -> confirm -> cancel)
# ==============================================================================


@pytest.mark.asyncio
async def test_valid_order_creation_flow(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Buyer creates an order: initializes in INITIATED state and reserves stock."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    payload = {
        "buyer_id": str(buyer.id),
        "listing_id": str(listing.id),
        "quantity": 100.0,
        "delivery_address": {
            "street": "123 Market Rd",
            "pincode": "143001",
            "district": "Amritsar",
            "state": "Punjab",
        },
    }

    response = await async_client.post("/api/v1/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "INITIATED"
    assert Decimal(str(data["quantity"])) == Decimal("100.00")
    assert Decimal(str(data["unit_price"])) == Decimal("60.00")
    assert Decimal(str(data["total_amount"])) == Decimal("6000.00")
    assert "id" in data


@pytest.mark.asyncio
async def test_valid_order_confirmation_flow(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Buyer confirms order via escrow funding: transitions INITIATED -> IN_ESCROW."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 50.0,
            "delivery_address": {"city": "Amritsar"},
        },
    )
    order_id = create_resp.json()["id"]

    confirm_resp = await async_client.post(
        f"/api/v1/orders/{order_id}/confirm",
        json={"payment_method": "UPI", "gateway_transaction_id": "txn_upi_12345"},
    )
    assert confirm_resp.status_code == 200
    data = confirm_resp.json()
    assert data["status"] == "IN_ESCROW"
    assert data["escrow_status"] == "HELD"


@pytest.mark.asyncio
async def test_valid_order_cancellation_from_initiated(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Buyer cancels an unfunded order: transitions INITIATED -> CANCELLED."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 20.0,
            "delivery_address": {"city": "Amritsar"},
        },
    )
    order_id = create_resp.json()["id"]

    cancel_resp = await async_client.post(
        f"/api/v1/orders/{order_id}/cancel",
        json={"reason": "Changed my mind before payment"},
    )
    assert cancel_resp.status_code == 200
    data = cancel_resp.json()
    assert data["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_valid_order_cancellation_from_in_escrow_refunds_buyer(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Buyer cancels order in escrow: transitions to CANCELLED with REFUNDED escrow."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 40.0,
            "delivery_address": {"city": "Amritsar"},
        },
    )
    order_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/orders/{order_id}/confirm",
        json={"payment_method": "UPI", "gateway_transaction_id": "txn_123"},
    )

    cancel_resp = await async_client.post(
        f"/api/v1/orders/{order_id}/cancel",
        json={"reason": "Farmer cannot ship immediately"},
    )
    assert cancel_resp.status_code == 200
    data = cancel_resp.json()
    assert data["status"] == "CANCELLED"
    assert data["escrow_status"] == "REFUNDED"


# ==============================================================================
# INVALID TRANSITIONS REJECTED WITH 409 CONFLICT (error-handling-patterns)
# ==============================================================================


@pytest.mark.asyncio
async def test_cannot_transition_initiated_to_dispatched(
    async_client: AsyncClient,
    order_setup: dict,
    db_session: AsyncSession,
) -> None:
    """Reject transition: INITIATED -> DISPATCHED (must lock escrow before dispatch)."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 10.0,
        },
    )
    order_id = create_resp.json()["id"]

    resp = await async_client.post(
        f"/api/v1/orders/{order_id}/dispatch",
        json={"tracking_number": "TRK123"},
    )
    assert resp.status_code == 409
    assert "Invalid order state transition" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_transition_initiated_directly_to_released(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Reject transition: INITIATED -> RELEASED."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 10.0,
        },
    )
    order_id = create_resp.json()["id"]

    resp = await async_client.post(f"/api/v1/orders/{order_id}/release")
    assert resp.status_code == 409
    assert "Invalid order state transition" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_transition_in_escrow_directly_to_released(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Reject transition: IN_ESCROW -> RELEASED (must dispatch first)."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 15.0,
        },
    )
    order_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/orders/{order_id}/confirm",
        json={"payment_method": "UPI"},
    )

    resp = await async_client.post(f"/api/v1/orders/{order_id}/release")
    assert resp.status_code == 409
    assert "Invalid order state transition" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_transition_cancelled_to_in_escrow(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Reject transition: CANCELLED -> IN_ESCROW (cancelled order is terminal)."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 10.0,
        },
    )
    order_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/orders/{order_id}/cancel",
        json={"reason": "Cancelled"},
    )

    # Attempting to confirm a cancelled order must fail
    confirm_resp = await async_client.post(
        f"/api/v1/orders/{order_id}/confirm",
        json={"payment_method": "UPI"},
    )
    assert confirm_resp.status_code == 409
    assert "Invalid order state transition" in confirm_resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_transition_cancelled_to_dispatched(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Reject transition: CANCELLED -> DISPATCHED (cannot dispatch cancelled order)."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 10.0,
        },
    )
    order_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/orders/{order_id}/cancel", json={"reason": "Cancelled"}
    )

    resp = await async_client.post(f"/api/v1/orders/{order_id}/dispatch", json={})
    assert resp.status_code == 409
    assert "Invalid order state transition" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_cancel_already_dispatched_order(
    async_client: AsyncClient,
    order_setup: dict,
    db_session: AsyncSession,
) -> None:
    """Reject transition: DISPATCHED -> CANCELLED."""
    farmer = order_setup["farmer"]
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    # Directly seed an order in DISPATCHED state
    order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("30.00"),
        unit_price=Decimal("60.00"),
        total_amount=Decimal("1800.00"),
        status=OrderStatus.DISPATCHED,
    )
    db_session.add(order)
    await db_session.flush()

    cancel_resp = await async_client.post(
        f"/api/v1/orders/{order.id}/cancel",
        json={"reason": "Attempting late cancel"},
    )
    assert cancel_resp.status_code == 409
    assert "Invalid order state transition" in cancel_resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_cancel_or_modify_released_order(
    async_client: AsyncClient,
    order_setup: dict,
    db_session: AsyncSession,
) -> None:
    """Reject transition: RELEASED -> CANCELLED (released payout is final)."""
    farmer = order_setup["farmer"]
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("25.00"),
        unit_price=Decimal("60.00"),
        total_amount=Decimal("1500.00"),
        status=OrderStatus.RELEASED,
    )
    db_session.add(order)
    await db_session.flush()

    cancel_resp = await async_client.post(
        f"/api/v1/orders/{order.id}/cancel",
        json={"reason": "Attempt cancel after release"},
    )
    assert cancel_resp.status_code == 409
    assert "Invalid order state transition" in cancel_resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_cancel_delivered_verified_order(
    async_client: AsyncClient,
    order_setup: dict,
    db_session: AsyncSession,
) -> None:
    """Reject transition: DELIVERED_VERIFIED -> CANCELLED."""
    farmer = order_setup["farmer"]
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("10.00"),
        unit_price=Decimal("60.00"),
        total_amount=Decimal("600.00"),
        status=OrderStatus.DELIVERED_VERIFIED,
    )
    db_session.add(order)
    await db_session.flush()

    resp = await async_client.post(
        f"/api/v1/orders/{order.id}/cancel",
        json={"reason": "Cannot cancel verified delivery"},
    )
    assert resp.status_code == 409
    assert "Invalid order state transition" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_dispatch_released_order(
    async_client: AsyncClient,
    order_setup: dict,
    db_session: AsyncSession,
) -> None:
    """Reject transition: RELEASED -> DISPATCHED (terminal state)."""
    farmer = order_setup["farmer"]
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("10.00"),
        unit_price=Decimal("60.00"),
        total_amount=Decimal("600.00"),
        status=OrderStatus.RELEASED,
    )
    db_session.add(order)
    await db_session.flush()

    resp = await async_client.post(
        f"/api/v1/orders/{order.id}/dispatch",
        json={"tracking_number": "TRK999"},
    )
    assert resp.status_code == 409
    assert "Invalid order state transition" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_cannot_release_cancelled_order(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Reject transition: CANCELLED -> RELEASED."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]

    create_resp = await async_client.post(
        "/api/v1/orders",
        json={
            "buyer_id": str(buyer.id),
            "listing_id": str(listing.id),
            "quantity": 10.0,
        },
    )
    order_id = create_resp.json()["id"]

    await async_client.post(
        f"/api/v1/orders/{order_id}/cancel", json={"reason": "Cancelled"}
    )

    resp = await async_client.post(f"/api/v1/orders/{order_id}/release")
    assert resp.status_code == 409
    assert "Invalid order state transition" in resp.json()["detail"]



# ==============================================================================
# DOMAIN VALIDATION ERRORS (error-handling-patterns)
# ==============================================================================


@pytest.mark.asyncio
async def test_cannot_order_more_than_available_quantity(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Cannot place an order exceeding produce inventory."""
    buyer = order_setup["buyer"]
    listing = order_setup["listing"]  # total quantity is 1000.00

    payload = {
        "buyer_id": str(buyer.id),
        "listing_id": str(listing.id),
        "quantity": 1500.00,  # Exceeds 1000 kg inventory!
    }

    response = await async_client.post("/api/v1/orders", json=payload)
    assert response.status_code == 400
    assert "Insufficient produce inventory" in response.json()["detail"]


@pytest.mark.asyncio
async def test_seller_cannot_buy_their_own_produce(
    async_client: AsyncClient,
    order_setup: dict,
) -> None:
    """Seller attempting to purchase their own produce must be rejected with 400."""
    farmer = order_setup["farmer"]
    listing = order_setup["listing"]

    payload = {
        "buyer_id": str(farmer.id),  # Farmer ordering own listing!
        "listing_id": str(listing.id),
        "quantity": 10.0,
    }

    response = await async_client.post("/api/v1/orders", json=payload)
    assert response.status_code == 400
    assert "Cannot purchase your own produce" in response.json()["detail"]
