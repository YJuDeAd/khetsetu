import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import EscrowStatus, OrderStatus


class OrderCreate(BaseModel):
    buyer_id: uuid.UUID
    listing_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0)
    delivery_address: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class OrderConfirm(BaseModel):
    payment_method: str = Field(default="UPI", max_length=50)
    gateway_transaction_id: str | None = Field(default=None, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class OrderCancel(BaseModel):
    reason: str | None = Field(default=None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class OrderDispatch(BaseModel):
    tracking_number: str | None = Field(default=None, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    listing_id: uuid.UUID
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    platform_fee: Decimal = Decimal("0.00")
    status: OrderStatus
    delivery_address: dict[str, Any] = Field(default_factory=dict)
    escrow_status: EscrowStatus | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
