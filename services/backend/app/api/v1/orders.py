import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.order import (
    OrderCancel,
    OrderConfirm,
    OrderCreate,
    OrderDispatch,
    OrderResponse,
)
from app.services.order_state_machine import OrderStateMachine

router = APIRouter()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new produce order in INITIATED state",
)
async def create_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Buyer initiates an order and reserves inventory."""
    state_machine = OrderStateMachine(db)
    order = await state_machine.create_order(
        buyer_id=payload.buyer_id,
        listing_id=payload.listing_id,
        quantity=payload.quantity,
        delivery_address=payload.delivery_address,
    )
    return OrderResponse.model_validate(order)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details by ID",
)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Retrieve full details of an order."""
    state_machine = OrderStateMachine(db)
    order = await state_machine.get_order(order_id)
    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/confirm",
    response_model=OrderResponse,
    summary="Confirm order payment and lock funds in escrow (INITIATED -> IN_ESCROW)",
)
async def confirm_order(
    order_id: uuid.UUID,
    payload: OrderConfirm | None = None,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Buyer funds escrow: transitions order INITIATED -> IN_ESCROW."""
    state_machine = OrderStateMachine(db)
    payment_method = payload.payment_method if payload else "UPI"
    gateway_txn_id = payload.gateway_transaction_id if payload else None
    order = await state_machine.confirm_order(
        order_id=order_id,
        payment_method=payment_method,
        gateway_transaction_id=gateway_txn_id,
    )
    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel order, restore stock, and refund escrow if held",
)
async def cancel_order(
    order_id: uuid.UUID,
    payload: OrderCancel | None = None,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Cancel order, restoring stock and refunding escrow if held."""
    state_machine = OrderStateMachine(db)
    reason = payload.reason if payload else None
    order = await state_machine.cancel_order(order_id=order_id, reason=reason)
    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/dispatch",
    response_model=OrderResponse,
    summary="Dispatch order (IN_ESCROW -> DISPATCHED)",
)
async def dispatch_order(
    order_id: uuid.UUID,
    payload: OrderDispatch | None = None,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Seller marks order as dispatched with optional tracking."""
    state_machine = OrderStateMachine(db)
    tracking_number = payload.tracking_number if payload else None
    order = await state_machine.dispatch_order(
        order_id=order_id, tracking_number=tracking_number
    )
    return OrderResponse.model_validate(order)


@router.post(
    "/{order_id}/release",
    response_model=OrderResponse,
    summary="Release escrow payment (DELIVERED_VERIFIED -> RELEASED)",
)
async def release_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Release escrow payout to seller once delivery is verified."""
    state_machine = OrderStateMachine(db)
    order = await state_machine.release_order(order_id=order_id)
    return OrderResponse.model_validate(order)
