from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.telemetry_hub import telemetry_hub

router = APIRouter(tags=["telemetry"])

@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await telemetry_hub.connect(websocket)
    try:
        while True:
            # Client can send ping or custom subscription preferences
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        telemetry_hub.disconnect(websocket)
    except Exception:
        telemetry_hub.disconnect(websocket)
