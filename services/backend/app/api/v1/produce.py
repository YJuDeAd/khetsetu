import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import ProduceStatus, UserRole
from app.models.produce import Produce
from app.models.user import User
from app.schemas.produce import ProduceCreate, ProduceResponse

router = APIRouter()


@router.post(
    "",
    response_model=ProduceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a produce listing",
)
async def create_listing(
    payload: ProduceCreate,
    db: AsyncSession = Depends(get_db),
) -> Produce:
    """Farmer or FPO creates a new produce listing."""
    # 1. Validate seller exists
    seller = await db.get(User, payload.seller_id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )

    # 2. Enforce role permission: only FARMER or FPO can list produce
    if seller.role not in (UserRole.FARMER, UserRole.FPO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers or FPOs can list produce",
        )

    # 3. Create listing record
    listing = Produce(
        seller_id=payload.seller_id,
        crop_name=payload.crop_name,
        crop_category=payload.crop_category,
        quantity=payload.quantity,
        unit=payload.unit,
        price_per_unit=payload.price_per_unit,
        harvest_date=payload.harvest_date,
        shelf_life_days=payload.shelf_life_days,
        status=ProduceStatus.ACTIVE,
        location_pincode=payload.location_pincode,
        location_district=payload.location_district,
        location_state=payload.location_state,
        location_lat=payload.location_lat,
        location_lng=payload.location_lng,
        attributes=payload.attributes,
    )

    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    return listing


@router.get(
    "",
    response_model=list[ProduceResponse],
    summary="Browse and filter produce listings",
)
async def list_produce(
    crop_name: str | None = Query(None, description="Search by crop name"),
    crop_category: str | None = Query(None, description="Filter by crop category"),
    location_state: str | None = Query(None, description="Filter by state"),
    location_district: str | None = Query(None, description="Filter by district"),
    min_price: Decimal | None = Query(None, ge=0, description="Minimum price per unit"),
    max_price: Decimal | None = Query(None, ge=0, description="Maximum price per unit"),
    produce_status: ProduceStatus = Query(
        ProduceStatus.ACTIVE,
        alias="status",
        description="Filter by listing status",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[Produce]:
    """Search and browse produce listings with flexible filtering."""
    query = select(Produce).where(Produce.status == produce_status)

    if crop_name:
        query = query.where(Produce.crop_name.ilike(f"%{crop_name}%"))
    if crop_category:
        query = query.where(Produce.crop_category.ilike(f"%{crop_category}%"))
    if location_state:
        query = query.where(Produce.location_state.ilike(f"%{location_state}%"))
    if location_district:
        query = query.where(Produce.location_district.ilike(f"%{location_district}%"))
    if min_price is not None:
        query = query.where(Produce.price_per_unit >= min_price)
    if max_price is not None:
        query = query.where(Produce.price_per_unit <= max_price)

    query = query.order_by(Produce.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get(
    "/{listing_id}",
    response_model=ProduceResponse,
    summary="Get single produce listing details",
)
async def get_listing(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Produce:
    """Retrieve full details of a specific produce listing by ID."""
    listing = await db.get(Produce, listing_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )
    return listing
