import asyncio
from datetime import datetime
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from core.config import settings

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.recent_events: List[dict] = []
        self.loop = None

    async def connect(self, websocket: WebSocket):
        self.loop = asyncio.get_running_loop()
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_recent_events(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def publish(self, message: dict):
        self._remember(message)
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast(message), self.loop)

    async def broadcast(self, message: dict):
        self._remember(message)
        await self._broadcast(message)

    async def send_recent_events(self, websocket: WebSocket):
        for event in self.recent_events:
            await websocket.send_text(json.dumps(event))

    def _remember(self, message: dict):
        enriched_message = dict(message)
        enriched_message.setdefault("server_time", datetime.utcnow().isoformat())
        self.recent_events.append(enriched_message)
        if len(self.recent_events) > settings.DASHBOARD_EVENT_BUFFER_SIZE:
            self.recent_events = self.recent_events[-settings.DASHBOARD_EVENT_BUFFER_SIZE:]

    async def _broadcast(self, message: dict):
        text_data = json.dumps(message)
        stale_connections: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(text_data)
            except RuntimeError:
                stale_connections.append(connection)

        for connection in stale_connections:
            self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # In a real app we might process incoming dashboard commands here
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
