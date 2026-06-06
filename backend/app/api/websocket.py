from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dependencies import ws_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/market")
async def market_ws(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "subscribe" and message.get("symbol"):
                ws_manager.symbols.add(message["symbol"])
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
