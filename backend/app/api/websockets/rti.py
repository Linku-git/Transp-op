from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

# Connected WebSocket clients per vehicle_id
_connections: dict[str, set[WebSocket]] = {}


@router.websocket("/ws/rti/{vehicle_id}")
async def rti_websocket(websocket: WebSocket, vehicle_id: str):
    """WebSocket endpoint for real-time vehicle position updates."""
    await websocket.accept()

    if vehicle_id not in _connections:
        _connections[vehicle_id] = set()
    _connections[vehicle_id].add(websocket)

    logger.info(f"WebSocket connected for vehicle {vehicle_id}")

    try:
        while True:
            # Keep connection alive, receive heartbeats
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for vehicle {vehicle_id}")
    finally:
        _connections.get(vehicle_id, set()).discard(websocket)
        if vehicle_id in _connections and not _connections[vehicle_id]:
            del _connections[vehicle_id]


async def broadcast_position(vehicle_id: str, position_data: dict) -> None:
    """Broadcast position update to all connected clients for a vehicle."""
    clients = _connections.get(vehicle_id, set()).copy()
    if not clients:
        return

    message = json.dumps({"type": "vehicle_position", "data": position_data})
    disconnected = set()

    for ws in clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)

    for ws in disconnected:
        _connections.get(vehicle_id, set()).discard(ws)
