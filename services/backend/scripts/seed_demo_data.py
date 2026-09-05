"""Seed script to populate initial demo data for KhetSetu manual testing.

Creates:
1. Demo Farmer (ID: 00000000-0000-0000-0000-000000000001)
2. Demo Buyer (ID: 00000000-0000-0000-0000-000000000002)
3. Three initial Produce Listings (Basmati Rice, Wheat, Tomatoes)
"""

import asyncio
import os
import sys
import uuid
from datetime import date
from decimal import Decimal

# Ensure backend root is on sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy import select  # noqa: E402

from app.core.database import AsyncSessionLocal, engine  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.models.enums import ProduceStatus, UserRole  # noqa: E402
from app.models.produce import Produce  # noqa: E402
from app.models.user import User  # noqa: E402

FARMER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
BUYER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


async def seed() -> None:
    print("[INFO] Connecting to database to seed demo data...")

    # Ensure tables exist (especially helpful for local sqlite development)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create Demo Farmer
        farmer = await session.get(User, FARMER_ID)
        if not farmer:
            farmer = User(
                id=FARMER_ID,
                phone_number="+919876543210",
                hashed_password="demo_hashed_password",
                full_name="Ramesh Kumar (Farmer)",
                role=UserRole.FARMER,
            )
            session.add(farmer)
            print(f"  [OK] Created Demo Farmer: {farmer.full_name} ({FARMER_ID})")
        else:
            print(f"  [INFO] Demo Farmer already exists: {farmer.full_name}")

        # 2. Create Demo Buyer
        buyer = await session.get(User, BUYER_ID)
        if not buyer:
            buyer = User(
                id=BUYER_ID,
                phone_number="+919876543211",
                hashed_password="demo_hashed_password",
                full_name="Anand Wholesale Mart (Buyer)",
                role=UserRole.BUYER,
            )
            session.add(buyer)
            print(f"  [OK] Created Demo Buyer: {buyer.full_name} ({BUYER_ID})")
        else:
            print(f"  [INFO] Demo Buyer already exists: {buyer.full_name}")

        await session.flush()

        # 3. Create Sample Produce Listings
        stmt = select(Produce).where(Produce.seller_id == FARMER_ID)
        existing_produce = (await session.execute(stmt)).scalars().all()

        if not existing_produce:
            listings = [
                Produce(
                    seller_id=FARMER_ID,
                    crop_name="Premium Basmati Rice",
                    crop_category="Cereals",
                    quantity=Decimal("500.00"),
                    unit="kg",
                    price_per_unit=Decimal("65.00"),
                    harvest_date=date.today(),
                    shelf_life_days=365,
                    status=ProduceStatus.ACTIVE,
                    location_pincode="143001",
                    location_district="Amritsar",
                    location_state="Punjab",
                    attributes={
                        "variety": "1121 Extra Long",
                        "is_organic": True,
                        "moisture_pct": 11.5,
                    },
                ),
                Produce(
                    seller_id=FARMER_ID,
                    crop_name="Sharbati Whole Wheat",
                    crop_category="Cereals",
                    quantity=Decimal("1200.00"),
                    unit="kg",
                    price_per_unit=Decimal("38.50"),
                    harvest_date=date.today(),
                    shelf_life_days=180,
                    status=ProduceStatus.ACTIVE,
                    location_pincode="462001",
                    location_district="Sehore",
                    location_state="Madhya Pradesh",
                    attributes={
                        "variety": "Sehore Golden",
                        "is_organic": False,
                    },
                ),
                Produce(
                    seller_id=FARMER_ID,
                    crop_name="Organic Desi Tomatoes",
                    crop_category="Vegetables",
                    quantity=Decimal("350.00"),
                    unit="kg",
                    price_per_unit=Decimal("28.00"),
                    harvest_date=date.today(),
                    shelf_life_days=14,
                    status=ProduceStatus.ACTIVE,
                    location_pincode="411001",
                    location_district="Pune",
                    location_state="Maharashtra",
                    attributes={
                        "variety": "Desi Sour",
                        "is_organic": True,
                    },
                ),
            ]
            session.add_all(listings)
            print(f"  [OK] Created {len(listings)} sample produce listings.")
        else:
            print(f"  [INFO] {len(existing_produce)} produce listings already present.")

        await session.commit()

    print("\n[SUCCESS] Database successfully seeded!")
    print(f"Demo Farmer ID : {FARMER_ID}")
    print(f"Demo Buyer ID  : {BUYER_ID}")


if __name__ == "__main__":
    asyncio.run(seed())
