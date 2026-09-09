import asyncio
import dataclasses
import json
from typing import List

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from api.config import settings
from firewall.event_bus import EventBus

router = APIRouter(prefix="/api/v1/ws", tags=["WebSockets"])
event_bus = EventBus()


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        from datetime import datetime

        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, api_key: str):
        if api_key != settings.API_KEY:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return False

        await websocket.accept()
        self.active_connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                # Connection might be already closed or dropping
                pass


manager = ConnectionManager()


# Background task to stream events to all clients
async def broadcast_events():
    alerts_queue = event_bus.subscribe_async("alerts")
    events_queue = event_bus.subscribe_async("events")

    try:
        while True:
            alert_task = asyncio.create_task(alerts_queue.get())
            event_task = asyncio.create_task(events_queue.get())

            done, pending = await asyncio.wait(
                [alert_task, event_task], return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

            for task in done:
                msg = task.result()
                msg_dict = json.loads(json.dumps(msg, cls=EnhancedJSONEncoder))
                topic = "alert" if getattr(msg, "alert_type", None) else "event"

                payload = {"topic": topic, "data": msg_dict}
                await manager.broadcast_json(payload)

    except asyncio.CancelledError:
        pass
    finally:
        event_bus.unsubscribe_async("alerts", alerts_queue)
        event_bus.unsubscribe_async("events", events_queue)


# Store the background task so we can start it when the app starts
broadcast_task = None


@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket, api_key: str = Query(None)):
    connected = await manager.connect(websocket, api_key)
    if not connected:
        return

    try:
        while True:
            # Simple heartbeat loop. Wait for client to send a ping or message.
            # You could also implement server-to-client pinging.
            data = await asyncio.wait_for(
                websocket.receive_text(), timeout=settings.WEBSOCKET_HEARTBEAT_INTERVAL
            )
            if data == "ping":
                await websocket.send_text("pong")
    except asyncio.TimeoutError:
        # Heartbeat missed, close connection to free up resources
        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
        manager.disconnect(websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
