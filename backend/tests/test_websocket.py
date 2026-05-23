from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_websocket_connects_and_returns_connected():
    with client.websocket_connect("/ws/test-session") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "connected"
        assert msg["session_id"] == "test-session"


def test_websocket_echo_command():
    with client.websocket_connect("/ws/echo-session") as ws:
        ws.receive_json()  # connected
        ws.send_json({"type": "command", "id": "1", "tool": "echo", "args": {"text": "ping"}})
        msg = ws.receive_json()
        assert msg["type"] == "result"
        assert msg["ok"] is True
        assert msg["data"] == "ping"


def test_websocket_ping_pong():
    with client.websocket_connect("/ws/ping-session") as ws:
        ws.receive_json()  # connected
        ws.send_json({"type": "pong"})
        # Should not crash; heartbeat continues in background
