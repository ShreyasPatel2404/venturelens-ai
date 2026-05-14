"""
VentureLens AI — WebSocket Manager
Broadcasts real-time agent progress events to connected frontend clients.
Each analysis session gets its own session_id so multiple tabs don't cross-talk.
"""

import json
import logging
from typing import Dict
from fastapi import WebSocket

logger = logging.getLogger("VentureLens.WS")


class ConnectionManager:
    def __init__(self):
        # session_id → WebSocket
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[session_id] = websocket
        logger.info(f"WS connected: {session_id}")

    def disconnect(self, session_id: str):
        self.active.pop(session_id, None)
        logger.info(f"WS disconnected: {session_id}")

    async def send(self, session_id: str, payload: dict):
        ws = self.active.get(session_id)
        if ws:
            try:
                await ws.send_text(json.dumps(payload))
            except Exception as e:
                logger.warning(f"WS send failed for {session_id}: {e}")
                self.disconnect(session_id)

    async def broadcast_progress(
        self,
        session_id: str,
        stage: str,
        status: str,          # "waiting" | "running" | "done" | "error"
        message: str = "",
    ):
        await self.send(session_id, {
            "type": "progress",
            "stage": stage,
            "status": status,
            "message": message,
        })

    async def broadcast_result(self, session_id: str, result: dict):
        await self.send(session_id, {"type": "result", "data": result})

    async def broadcast_error(self, session_id: str, error: str):
        await self.send(session_id, {"type": "error", "message": error})


# Singleton used by both main.py and pipeline.py
manager = ConnectionManager()