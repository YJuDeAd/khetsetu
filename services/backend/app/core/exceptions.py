class DomainError(Exception):
    """Base domain exception for KhetSetu application."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidOrderStateTransitionError(DomainError):
    """Raised when an illegal order or escrow state transition is attempted."""


class InsufficientInventoryError(DomainError):
    """Raised when requested quantity exceeds available produce inventory."""


class SelfPurchaseError(DomainError):
    """Raised when a seller attempts to buy their own produce listing."""


class EntityNotFoundError(DomainError):
    """Raised when a requested domain entity is not found."""
