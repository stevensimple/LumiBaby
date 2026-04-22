import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.events.engine import manager
from app.middleware.auth import decode_token
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket, token: str = Query(None)):
    if settings.enable_auth:
        if not token:
            await websocket.close(code=4001)
            return
        try:
            decode_token(token)
        except Exception:
            await websocket.close(code=4001)
            return

    await manager.connect(websocket)
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=35.0)
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type": "ping"}))
            except Exception:
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)
