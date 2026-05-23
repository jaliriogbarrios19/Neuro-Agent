"""Neuro Agent Backend — sidecar process for the Tauri desktop app."""

import asyncio
import uuid
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.agent.agent import NeuroAgent

app = FastAPI(title="Neuro Agent Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = NeuroAgent()
_sessions: dict[str, WebSocket] = {}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(ws: WebSocket, session_id: str):
    await ws.accept()
    _sessions[session_id] = ws

    await ws.send_json({"type": "connected", "session_id": session_id})

    async def heartbeat():
        while session_id in _sessions:
            await asyncio.sleep(15)
            try:
                if session_id in _sessions:
                    await ws.send_json({"type": "ping"})
            except Exception:
                break

    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        while True:
            data: dict[str, Any] = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "pong":
                continue
            elif msg_type == "command":
                req_id = data.get("id", str(uuid.uuid4()))
                result = await agent.handle_message(data)
                result["id"] = req_id
                await ws.send_json({"type": "result", **result})
    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()
        _sessions.pop(session_id, None)


async def main():
    import uvicorn

    config = uvicorn.Config(app, host="127.0.0.1", port=9876, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
