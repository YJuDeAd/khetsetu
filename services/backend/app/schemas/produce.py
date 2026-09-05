import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ProduceStatus


class ProduceBase(BaseModel):
    crop_name: str = Field(..., min_length=2, max_length=100)
    crop_category: str = Field(..., min_length=2, max_length=50)
    quantity: Decimal = Field(..., gt=0)
    unit: str = Field(default="kg", max_length=20)
    price_per_unit: Decimal = Field(..., gt=0)
    harvest_date: date
    shelf_life_days: int = Field(default=7, gt=0)
    location_pincode: str = Field(..., max_length=10)
    location_district: str = Field(..., max_length=100)
    location_state: str = Field(..., max_length=100)
    location_lat: Decimal | None = None
    location_lng: Decimal | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ProduceCreate(ProduceBase):
    seller_id: uuid.UUID


class ProduceResponse(ProduceBase):
    id: uuid.UUID
    seller_id: uuid.UUID
    status: ProduceStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
