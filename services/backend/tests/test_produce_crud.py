import uuid
from datetime import date
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Produce, ProduceStatus, User, UserRole


@pytest.mark.asyncio
async def test_farmer_can_create_produce_listing(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Farmer should successfully create a produce listing with JSONB attributes."""
    farmer = User(
        phone_number="+919876543201",
        hashed_password="hashed_pw",
        full_name="Harpreet Singh",
        role=UserRole.FARMER,
        preferred_language="pa",
    )
    db_session.add(farmer)
    await db_session.flush()

    payload = {
        "seller_id": str(farmer.id),
        "crop_name": "Sharbati Wheat",
        "crop_category": "Cereals",
        "quantity": 1500.00,
        "unit": "kg",
        "price_per_unit": 32.50,
        "harvest_date": str(date.today()),
        "shelf_life_days": 180,
        "location_pincode": "141001",
        "location_district": "Ludhiana",
        "location_state": "Punjab",
        "attributes": {
            "variety": "Sharbati",
            "organic_certified": True,
            "grade": "A+",
            "moisture_percentage": 11.5,
        },
    }

    response = await async_client.post("/api/v1/listings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["crop_name"] == "Sharbati Wheat"
    assert data["status"] == "ACTIVE"
    assert Decimal(str(data["price_per_unit"])) == Decimal("32.50")
    assert data["attributes"]["organic_certified"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_buyer_cannot_create_produce_listing(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A buyer account must be rejected with 403 when trying to list produce."""
    buyer = User(
        phone_number="+919876543202",
        hashed_password="hashed_pw",
        full_name="Reliance Retail Buyer",
        role=UserRole.BUYER,
    )
    db_session.add(buyer)
    await db_session.flush()

    payload = {
        "seller_id": str(buyer.id),
        "crop_name": "Tomatoes",
        "crop_category": "Vegetables",
        "quantity": 200.0,
        "unit": "kg",
        "price_per_unit": 20.0,
        "harvest_date": str(date.today()),
        "shelf_life_days": 7,
        "location_pincode": "110001",
        "location_district": "Central Delhi",
        "location_state": "Delhi",
    }

    response = await async_client.post("/api/v1/listings", json=payload)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_listing_creation_fails_with_invalid_seller_id(
    async_client: AsyncClient,
) -> None:
    """Attempting to list produce under a non-existent seller must return 404."""
    payload = {
        "seller_id": str(uuid.uuid4()),
        "crop_name": "Potatoes",
        "crop_category": "Vegetables",
        "quantity": 100.0,
        "unit": "kg",
        "price_per_unit": 15.0,
        "harvest_date": str(date.today()),
        "shelf_life_days": 30,
        "location_pincode": "282001",
        "location_district": "Agra",
        "location_state": "Uttar Pradesh",
    }

    response = await async_client.post("/api/v1/listings", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Seller not found"


@pytest.mark.asyncio
async def test_listing_creation_validates_positive_price_and_quantity(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Request validation must return 422 if quantity or price is non-positive."""
    farmer = User(
        phone_number="+919876543203",
        hashed_password="hashed_pw",
        full_name="Sanjay Farmer",
        role=UserRole.FARMER,
    )
    db_session.add(farmer)
    await db_session.flush()

    payload = {
        "seller_id": str(farmer.id),
        "crop_name": "Basmati Rice",
        "crop_category": "Cereals",
        "quantity": -50.0,  # Invalid negative quantity
        "unit": "kg",
        "price_per_unit": 0.0,  # Invalid zero price
        "harvest_date": str(date.today()),
        "shelf_life_days": 180,
        "location_pincode": "132001",
        "location_district": "Karnal",
        "location_state": "Haryana",
    }

    response = await async_client.post("/api/v1/listings", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_buyer_can_browse_and_filter_listings(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Buyer queries active listings filtered by crop, price, and location."""
    farmer = User(
        phone_number="+919876543204",
        hashed_password="hashed_pw",
        full_name="Vikram Farmer",
        role=UserRole.FARMER,
    )
    db_session.add(farmer)
    await db_session.flush()

    # Seed listings
    listing1 = Produce(
        seller_id=farmer.id,
        crop_name="Alphonso Mango",
        crop_category="Fruits",
        quantity=Decimal("500.00"),
        unit="box",
        price_per_unit=Decimal("800.00"),
        harvest_date=date.today(),
        shelf_life_days=14,
        status=ProduceStatus.ACTIVE,
        location_pincode="415612",
        location_district="Ratnagiri",
        location_state="Maharashtra",
        attributes={"grade": "Export"},
    )
    listing2 = Produce(
        seller_id=farmer.id,
        crop_name="Nagpur Orange",
        crop_category="Fruits",
        quantity=Decimal("1200.00"),
        unit="kg",
        price_per_unit=Decimal("60.00"),
        harvest_date=date.today(),
        shelf_life_days=20,
        status=ProduceStatus.ACTIVE,
        location_pincode="440001",
        location_district="Nagpur",
        location_state="Maharashtra",
        attributes={"sweetness_brix": 12},
    )
    listing3 = Produce(
        seller_id=farmer.id,
        crop_name="Kashmiri Apple",
        crop_category="Fruits",
        quantity=Decimal("2000.00"),
        unit="kg",
        price_per_unit=Decimal("120.00"),
        harvest_date=date.today(),
        shelf_life_days=45,
        status=ProduceStatus.ACTIVE,
        location_pincode="190001",
        location_district="Srinagar",
        location_state="Jammu and Kashmir",
        attributes={"cold_chain_required": True},
    )
    db_session.add_all([listing1, listing2, listing3])
    await db_session.flush()

    # 1. Query all fruits
    response = await async_client.get("/api/v1/listings?crop_category=Fruits")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3

    # 2. Filter by crop name search (Alphonso)
    response = await async_client.get("/api/v1/listings?crop_name=Mango")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["crop_name"] == "Alphonso Mango"

    # 3. Filter by state (Maharashtra)
    response = await async_client.get("/api/v1/listings?location_state=Maharashtra")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2

    # 4. Filter by price range
    response = await async_client.get("/api/v1/listings?min_price=50&max_price=100")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["crop_name"] == "Nagpur Orange"


@pytest.mark.asyncio
async def test_get_listing_by_id(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Fetching an existing listing by ID returns 200, non-existent returns 404."""
    farmer = User(
        phone_number="+919876543205",
        hashed_password="hashed_pw",
        full_name="Gurpreet Farmer",
        role=UserRole.FPO,
    )
    db_session.add(farmer)
    await db_session.flush()

    listing = Produce(
        seller_id=farmer.id,
        crop_name="Basmati 1121",
        crop_category="Cereals",
        quantity=Decimal("5000.00"),
        unit="quintal",
        price_per_unit=Decimal("4500.00"),
        harvest_date=date.today(),
        shelf_life_days=365,
        status=ProduceStatus.ACTIVE,
        location_pincode="143001",
        location_district="Amritsar",
        location_state="Punjab",
        attributes={"grain_length_mm": 8.4, "aged_years": 1},
    )
    db_session.add(listing)
    await db_session.flush()

    # Success case
    response = await async_client.get(f"/api/v1/listings/{listing.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(listing.id)
    assert data["crop_name"] == "Basmati 1121"
    assert data["attributes"]["grain_length_mm"] == 8.4

    # 404 case
    response = await async_client.get(f"/api/v1/listings/{uuid.uuid4()}")
    assert response.status_code == 404
