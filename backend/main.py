import asyncio
import time
import json
import contextlib
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from backend.packet_listener import PacketListener

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()
listener = None
start_time = time.time()
loop = None

def trigger_alert(alert: dict):
    # Route cross-thread invocation to FastAPI's asyncio event loop
    if loop is not None and loop.is_running():
        asyncio.run_coroutine_threadsafe(manager.broadcast(alert), loop)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global listener, loop
    loop = asyncio.get_running_loop()
    
    print("[*] Initializing NIDS Scapy Packet Listener...")
    listener = PacketListener(alert_callback=trigger_alert)
    listener.start()
    
    yield
    listener.stop()

app = FastAPI(lifespan=lifespan)

@app.get("/metrics")
def get_metrics():
    return {
        "uptime_seconds": round(time.time() - start_time, 2),
        "total_packets_analyzed": listener.total_packets_analyzed if listener else 0,
        "total_threats_blocked": listener.total_threats if listener else 0,
        "active_flows": len(listener.tracker.flows) if listener else 0
    }

@app.post("/test_alert")
async def test_alert(alert: dict):
    """Endpoint for the test script to push simulated attack alerts to the dashboard."""
    if listener:
        listener.total_threats += 1
    await manager.broadcast(alert)
    return {"status": "alert_broadcast"}

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
