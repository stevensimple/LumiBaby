import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Set

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._connections: Set = set()

    async def connect(self, websocket):
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket):
        self._connections.discard(websocket)

    async def broadcast(self, message: dict):
        if not self._connections:
            return
        data = json.dumps(message)
        dead = set()
        for ws in list(self._connections):
            try:
                await ws.send_text(data)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections.discard(ws)

    async def broadcast_status(self, status: dict):
        await self.broadcast({"type": "status_update", "data": status})

    async def broadcast_event(self, event_type: str, sensor_id: str, details: dict):
        await self.broadcast({
            "type": "event",
            "event": {
                "id": str(uuid.uuid4()),
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "sensor_id": sensor_id,
                "details": details,
            }
        })

    async def broadcast_alert(self, alert_type: str, message: str, severity: str = "warning", sensor_id: str = None):
        await self.broadcast({
            "type": "alert",
            "alert": {
                "id": str(uuid.uuid4()),
                "type": alert_type,
                "message": message,
                "severity": severity,
                "sensor_id": sensor_id,
            }
        })

manager = ConnectionManager()
