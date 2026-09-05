import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """In-memory WebSocket connection manager for real-time order/driver telemetry."""

    def __init__(self) -> None:
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, topic: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if topic not in self.active_connections:
            self.active_connections[topic] = set()
        self.active_connections[topic].add(websocket)
        logger.info(f"WebSocket client connected to topic: {topic}")

    def disconnect(self, topic: str, websocket: WebSocket) -> None:
        if topic in self.active_connections:
            self.active_connections[topic].discard(websocket)
            if not self.active_connections[topic]:
                del self.active_connections[topic]
        logger.info(f"WebSocket client disconnected from topic: {topic}")

    async def broadcast_to_topic(self, topic: str, message: dict[str, Any]) -> None:
        if topic in self.active_connections:
            disconnected = []
            for connection in self.active_connections[topic]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            for dead_conn in disconnected:
                self.disconnect(topic, dead_conn)


ws_manager = ConnectionManager()


@router.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str) -> None:
    """Native FastAPI WebSocket endpoint for live notifications and telemetry."""
    await ws_manager.connect(topic, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back with confirmation or telemetry acknowledgement
            await websocket.send_json(
                {"event": "ack", "topic": topic, "received": data}
            )
    except WebSocketDisconnect:
        ws_manager.disconnect(topic, websocket)
