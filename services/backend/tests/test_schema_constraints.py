import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DeliveryRoute,
    EscrowStatus,
    Order,
    Payment,
    Produce,
    RouteStop,
    StopStatus,
    StopType,
    User,
    UserRole,
)


@pytest.mark.asyncio
async def test_cannot_create_order_with_negative_or_zero_quantity(
    db_session: AsyncSession,
) -> None:
    """Ensure chk_order_positive_quantity prevents non-positive order quantity."""
    farmer = User(
        phone_number="+919876543210",
        hashed_password="hash",
        full_name="Ramesh Farmer",
        role=UserRole.FARMER,
    )
    buyer = User(
        phone_number="+919876543211",
        hashed_password="hash",
        full_name="Suresh Buyer",
        role=UserRole.BUYER,
    )
    db_session.add_all([farmer, buyer])
    await db_session.flush()

    listing = Produce(
        seller_id=farmer.id,
        crop_name="Wheat",
        crop_category="Cereals",
        quantity=Decimal("1000.00"),
        price_per_unit=Decimal("25.00"),
        harvest_date=date.today(),
        shelf_life_days=90,
        location_pincode="141001",
        location_district="Ludhiana",
        location_state="Punjab",
    )
    db_session.add(listing)
    await db_session.flush()

    order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("-5.00"),
        unit_price=Decimal("25.00"),
        total_amount=Decimal("0.00"),
    )
    db_session.add(order)

    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_order_with_zero_or_negative_unit_price(
    db_session: AsyncSession,
) -> None:
    """Ensure chk_order_positive_unit_price prevents zero or negative unit price."""
    farmer = User(
        phone_number="+919876543212",
        hashed_password="hash",
        full_name="Farmer Two",
        role=UserRole.FARMER,
    )
    buyer = User(
        phone_number="+919876543213",
        hashed_password="hash",
        full_name="Buyer Two",
        role=UserRole.BUYER,
    )
    db_session.add_all([farmer, buyer])
    await db_session.flush()

    listing = Produce(
        seller_id=farmer.id,
        crop_name="Tomato",
        crop_category="Vegetables",
        quantity=Decimal("500.00"),
        price_per_unit=Decimal("15.00"),
        harvest_date=date.today(),
        shelf_life_days=7,
        location_pincode="422001",
        location_district="Nashik",
        location_state="Maharashtra",
    )
    db_session.add(listing)
    await db_session.flush()

    invalid_order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("50.00"),
        unit_price=Decimal("0.00"),
        total_amount=Decimal("0.00"),
    )
    db_session.add(invalid_order)

    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_produce_with_negative_quantity(
    db_session: AsyncSession,
) -> None:
    """Ensure chk_produce_non_negative_quantity prevents negative quantity."""
    farmer = User(
        phone_number="+919876543214",
        hashed_password="hash",
        full_name="Farmer Three",
        role=UserRole.FARMER,
    )
    db_session.add(farmer)
    await db_session.flush()

    invalid_produce = Produce(
        seller_id=farmer.id,
        crop_name="Rice",
        crop_category="Cereals",
        quantity=Decimal("-10.00"),
        price_per_unit=Decimal("40.00"),
        harvest_date=date.today(),
        shelf_life_days=180,
        location_pincode="132001",
        location_district="Karnal",
        location_state="Haryana",
    )
    db_session.add(invalid_produce)

    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_produce_with_zero_or_negative_price(
    db_session: AsyncSession,
) -> None:
    """Ensure chk_produce_positive_price prevents zero or negative price."""
    farmer = User(
        phone_number="+919876543215",
        hashed_password="hash",
        full_name="Farmer Four",
        role=UserRole.FARMER,
    )
    db_session.add(farmer)
    await db_session.flush()

    invalid_produce = Produce(
        seller_id=farmer.id,
        crop_name="Potato",
        crop_category="Vegetables",
        quantity=Decimal("100.00"),
        price_per_unit=Decimal("-5.00"),
        harvest_date=date.today(),
        shelf_life_days=30,
        location_pincode="282001",
        location_district="Agra",
        location_state="Uttar Pradesh",
    )
    db_session.add(invalid_produce)

    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_payment_with_zero_or_negative_amount(
    db_session: AsyncSession,
) -> None:
    """Ensure chk_payment_positive_amount prevents invalid funding amounts."""
    farmer = User(
        phone_number="+919876543216",
        hashed_password="hash",
        full_name="Farmer Five",
        role=UserRole.FARMER,
    )
    buyer = User(
        phone_number="+919876543217",
        hashed_password="hash",
        full_name="Buyer Five",
        role=UserRole.BUYER,
    )
    db_session.add_all([farmer, buyer])
    await db_session.flush()

    listing = Produce(
        seller_id=farmer.id,
        crop_name="Mustard",
        crop_category="Oilseeds",
        quantity=Decimal("200.00"),
        price_per_unit=Decimal("60.00"),
        harvest_date=date.today(),
        shelf_life_days=180,
        location_pincode="302001",
        location_district="Jaipur",
        location_state="Rajasthan",
    )
    db_session.add(listing)
    await db_session.flush()

    order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("10.00"),
        unit_price=Decimal("60.00"),
        total_amount=Decimal("600.00"),
    )
    db_session.add(order)
    await db_session.flush()

    invalid_payment = Payment(
        order_id=order.id,
        amount=Decimal("-100.00"),
        escrow_status=EscrowStatus.PENDING,
    )
    db_session.add(invalid_payment)

    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_route_where_load_exceeds_capacity(
    db_session: AsyncSession,
) -> None:
    """Ensure chk_route_load_within_capacity enforces vehicle capacity."""
    invalid_route = DeliveryRoute(
        vehicle_type="PICKUP_TRUCK",
        total_capacity_kg=Decimal("1000.00"),
        current_load_kg=Decimal("1500.00"),
        is_cold_chain=False,
    )
    db_session.add(invalid_route)

    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_duplicate_user_phone_number(
    db_session: AsyncSession,
) -> None:
    """Ensure unique constraint prevents duplicate user phone numbers."""
    phone = "+919999988888"
    user1 = User(
        phone_number=phone,
        hashed_password="hash",
        full_name="First User",
        role=UserRole.FARMER,
    )
    user2 = User(
        phone_number=phone,
        hashed_password="hash",
        full_name="Second User with Same Phone",
        role=UserRole.BUYER,
    )
    db_session.add(user1)
    await db_session.flush()

    db_session.add(user2)
    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_duplicate_route_stop_number(
    db_session: AsyncSession,
) -> None:
    """Ensure uq_route_stop_number prevents duplicate stops on same route."""
    farmer = User(
        phone_number="+919876543218",
        hashed_password="hash",
        full_name="Farmer Six",
        role=UserRole.FARMER,
    )
    buyer = User(
        phone_number="+919876543219",
        hashed_password="hash",
        full_name="Buyer Six",
        role=UserRole.BUYER,
    )
    db_session.add_all([farmer, buyer])
    await db_session.flush()

    listing = Produce(
        seller_id=farmer.id,
        crop_name="Onion",
        crop_category="Vegetables",
        quantity=Decimal("500.00"),
        price_per_unit=Decimal("20.00"),
        harvest_date=date.today(),
        shelf_life_days=30,
        location_pincode="422002",
        location_district="Nashik",
        location_state="Maharashtra",
    )
    db_session.add(listing)
    await db_session.flush()

    order = Order(
        buyer_id=buyer.id,
        seller_id=farmer.id,
        listing_id=listing.id,
        quantity=Decimal("100.00"),
        unit_price=Decimal("20.00"),
        total_amount=Decimal("2000.00"),
    )
    route = DeliveryRoute(
        vehicle_type="REEFER_VAN",
        total_capacity_kg=Decimal("2000.00"),
        current_load_kg=Decimal("100.00"),
        is_cold_chain=True,
    )
    db_session.add_all([order, route])
    await db_session.flush()

    stop1 = RouteStop(
        route_id=route.id,
        order_id=order.id,
        stop_number=1,
        stop_type=StopType.PICKUP,
        status=StopStatus.PENDING,
    )
    stop2 = RouteStop(
        route_id=route.id,
        order_id=order.id,
        stop_number=1,
        stop_type=StopType.DROPOFF,
        status=StopStatus.PENDING,
    )
    db_session.add(stop1)
    await db_session.flush()

    db_session.add(stop2)
    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_cannot_create_order_with_non_existent_foreign_keys(
    db_session: AsyncSession,
) -> None:
    """Ensure foreign key constraints prevent orphan orders."""
    fake_id = uuid.uuid4()
    invalid_order = Order(
        buyer_id=fake_id,
        seller_id=fake_id,
        listing_id=fake_id,
        quantity=Decimal("10.00"),
        unit_price=Decimal("20.00"),
        total_amount=Decimal("200.00"),
    )
    db_session.add(invalid_order)

    with pytest.raises(IntegrityError):
        await db_session.flush()
    await db_session.rollback()
