from fastapi import APIRouter

from app.api.v1 import orders, produce, websockets
from app.core.config import settings
from app.schemas.health import HealthResponse

api_router = APIRouter()


# Health check route
@api_router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.ENVIRONMENT,
    )


# Include v1 routes
api_router.include_router(produce.router, prefix="/listings", tags=["Listings"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(websockets.router, prefix="", tags=["WebSockets"])
