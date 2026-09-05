import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    EntityNotFoundError,
    InsufficientInventoryError,
    InvalidOrderStateTransitionError,
    SelfPurchaseError,
)
from app.models.enums import EscrowStatus, OrderStatus, ProduceStatus
from app.models.order import Order
from app.models.payment import Payment
from app.models.produce import Produce
from app.models.user import User

# Explicit Finite State Machine Definition
# Maps current OrderStatus to allowed next OrderStatus
VALID_ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.INITIATED: {
        OrderStatus.IN_ESCROW,
        OrderStatus.CANCELLED,
    },
    OrderStatus.IN_ESCROW: {
        OrderStatus.DISPATCHED,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED,
        OrderStatus.DISPUTED,
    },
    OrderStatus.DISPATCHED: {
        OrderStatus.DELIVERED_VERIFIED,
        OrderStatus.DISPUTED,
    },
    OrderStatus.DELIVERED_VERIFIED: {
        OrderStatus.RELEASED,
        OrderStatus.DISPUTED,
    },
    OrderStatus.RELEASED: set(),  # Terminal state
    OrderStatus.CANCELLED: set(),  # Terminal state
    OrderStatus.REFUNDED: set(),  # Terminal state
    OrderStatus.DISPUTED: {
        OrderStatus.REFUNDED,
        OrderStatus.RELEASED,
    },
}

# Explicit Escrow State Machine Definition
VALID_ESCROW_TRANSITIONS: dict[EscrowStatus, set[EscrowStatus]] = {
    EscrowStatus.PENDING: {
        EscrowStatus.HELD,
        EscrowStatus.REFUNDED,
    },
    EscrowStatus.HELD: {
        EscrowStatus.RELEASE_REQUESTED,
        EscrowStatus.RELEASED,
        EscrowStatus.REFUNDED,
        EscrowStatus.DISPUTED,
    },
    EscrowStatus.RELEASE_REQUESTED: {
        EscrowStatus.RELEASED,
        EscrowStatus.DISPUTED,
    },
    EscrowStatus.RELEASED: set(),
    EscrowStatus.REFUNDED: set(),
    EscrowStatus.DISPUTED: {
        EscrowStatus.RELEASED,
        EscrowStatus.REFUNDED,
    },
}


class OrderStateMachine:
    """Service implementing the explicit Order Lifecycle & Escrow State Machine."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_order(self, order_id: uuid.UUID) -> Order:
        """Fetch order with eager-loaded payment and listing relationships."""
        stmt = (
            select(Order)
            .options(selectinload(Order.payment), selectinload(Order.listing))
            .where(Order.id == order_id)
        )
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise EntityNotFoundError(f"Order with id {order_id} not found")
        return order

    def validate_transition(
        self, current_status: OrderStatus, target_status: OrderStatus
    ) -> None:
        """Validate state transition; raise 409 domain exception if illegal."""
        allowed_targets = VALID_ORDER_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_targets:
            msg = (
                f"Invalid order state transition from "
                f"{current_status.value} to {target_status.value}"
            )
            raise InvalidOrderStateTransitionError(msg)

    async def create_order(
        self,
        buyer_id: uuid.UUID,
        listing_id: uuid.UUID,
        quantity: Decimal,
        delivery_address: dict[str, Any] | None = None,
    ) -> Order:
        """Create an order in INITIATED state and reserve stock from listing."""
        buyer = await self.db.get(User, buyer_id)
        if not buyer:
            raise EntityNotFoundError(f"Buyer with id {buyer_id} not found")

        listing = await self.db.get(Produce, listing_id)
        if not listing:
            raise EntityNotFoundError(f"Produce listing with id {listing_id} not found")

        # Validation: Seller cannot buy their own produce
        if listing.seller_id == buyer_id:
            raise SelfPurchaseError("Cannot purchase your own produce")

        # Validation: Inventory check
        if quantity > listing.quantity:
            raise InsufficientInventoryError(
                f"Insufficient produce inventory. Requested: {quantity}, "
                f"Available: {listing.quantity}"
            )

        total_amount = quantity * listing.price_per_unit

        order = Order(
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            listing_id=listing_id,
            quantity=quantity,
            unit_price=listing.price_per_unit,
            total_amount=total_amount,
            platform_fee=Decimal("0.00"),
            status=OrderStatus.INITIATED,
            delivery_address=delivery_address or {},
        )
        self.db.add(order)

        payment = Payment(
            order=order,
            amount=total_amount,
            currency="INR",
            payment_method="UPI",
            escrow_status=EscrowStatus.PENDING,
        )
        self.db.add(payment)

        # Reserve inventory
        listing.quantity -= quantity
        if listing.quantity == Decimal("0.00"):
            listing.status = ProduceStatus.SOLD_OUT

        await self.db.commit()

        return await self.get_order(order.id)

    async def confirm_order(
        self,
        order_id: uuid.UUID,
        payment_method: str = "UPI",
        gateway_transaction_id: str | None = None,
    ) -> Order:
        """Transition order INITIATED -> IN_ESCROW and lock funds in escrow (HELD)."""
        order = await self.get_order(order_id)
        self.validate_transition(order.status, OrderStatus.IN_ESCROW)

        order.status = OrderStatus.IN_ESCROW
        if order.payment:
            order.payment.escrow_status = EscrowStatus.HELD
            order.payment.payment_method = payment_method
            order.payment.gateway_transaction_id = gateway_transaction_id
            order.payment.held_at = datetime.now(UTC)

        await self.db.commit()
        return await self.get_order(order.id)

    async def cancel_order(
        self,
        order_id: uuid.UUID,
        reason: str | None = None,
    ) -> Order:
        """Cancel order from INITIATED or IN_ESCROW state, restoring inventory."""
        order = await self.get_order(order_id)
        self.validate_transition(order.status, OrderStatus.CANCELLED)

        # Restore inventory
        listing = order.listing
        if not listing and order.listing_id:
            listing = await self.db.get(Produce, order.listing_id)

        if listing:
            listing.quantity += order.quantity
            if listing.status == ProduceStatus.SOLD_OUT and listing.quantity > 0:
                listing.status = ProduceStatus.ACTIVE

        order.status = OrderStatus.CANCELLED

        # Handle escrow refund if payment exists
        if order.payment:
            order.payment.escrow_status = EscrowStatus.REFUNDED
            order.payment.refunded_at = datetime.now(UTC)
            if reason:
                order.payment.metadata_json = {
                    **order.payment.metadata_json,
                    "cancellation_reason": reason,
                }

        await self.db.commit()
        return await self.get_order(order.id)

    async def dispatch_order(
        self,
        order_id: uuid.UUID,
        tracking_number: str | None = None,
    ) -> Order:
        """Transition order IN_ESCROW -> DISPATCHED."""
        order = await self.get_order(order_id)
        self.validate_transition(order.status, OrderStatus.DISPATCHED)

        order.status = OrderStatus.DISPATCHED
        if tracking_number and order.delivery_address is not None:
            order.delivery_address = {
                **order.delivery_address,
                "tracking_number": tracking_number,
            }

        await self.db.commit()
        return await self.get_order(order.id)

    async def verify_delivery(self, order_id: uuid.UUID) -> Order:
        """Transition order DISPATCHED -> DELIVERED_VERIFIED."""
        order = await self.get_order(order_id)
        self.validate_transition(order.status, OrderStatus.DELIVERED_VERIFIED)

        order.status = OrderStatus.DELIVERED_VERIFIED
        await self.db.commit()
        return await self.get_order(order.id)

    async def release_order(self, order_id: uuid.UUID) -> Order:
        """Transition order DELIVERED_VERIFIED -> RELEASED and disburse funds."""
        order = await self.get_order(order_id)
        self.validate_transition(order.status, OrderStatus.RELEASED)

        order.status = OrderStatus.RELEASED
        if order.payment:
            order.payment.escrow_status = EscrowStatus.RELEASED
            order.payment.released_at = datetime.now(UTC)

        await self.db.commit()
        return await self.get_order(order.id)
