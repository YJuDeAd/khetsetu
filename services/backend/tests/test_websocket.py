from starlette.testclient import TestClient


def test_native_websocket_connection(test_client: TestClient) -> None:
    """Verify native FastAPI WebSocket endpoint connects, sends, and receives data."""
    topic = "order_123"
    with test_client.websocket_connect(f"/api/v1/ws/{topic}") as websocket:
        websocket.send_text("status_ping")
        response = websocket.receive_json()
        assert response["event"] == "ack"
        assert response["topic"] == topic
        assert response["received"] == "status_ping"
