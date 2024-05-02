from fastapi import WebSocket, WebSocketDisconnect

from . import ws_router
from ..bot.openai_backend import SearchBot
from ..database import get_async_session


@ws_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    chatbot = SearchBot()
    session = await get_async_session()
    try:
        while True:
            data = await websocket.receive_json()
            await chatbot.ask_and_send(data, websocket, session)
    except WebSocketDisconnect:
        await session.commit()
        await session.close()
