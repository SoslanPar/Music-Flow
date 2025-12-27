from fastapi import APIRouter, WebSocket
from dependencies import ws_routes

router = APIRouter()

@router.websocket("/room/{room_id}/ws")
async def room_websocket(websocket: WebSocket, room_id: str, user_id: str):
    if not user_id:
        await websocket.close(code=4001, reason="User ID cookie required")
        return
    await ws_routes.handle_websocket(websocket, room_id, user_id)
