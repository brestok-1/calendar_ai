from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect

from . import ws_router
from .bots import PredictionBot
from ..auth import get_current_user
from ..database import get_async_session


@ws_router.websocket("/ws/search-product-test/{timezone}")
async def search_products_test(request: Request, websocket: WebSocket, timezone: str):
    await websocket.accept()
    chatbot = PredictionBot(timezone)
    user, credentials = await get_current_user(request)
    session = await get_async_session()
    try:
        while True:
            data = await websocket.receive_json()
            data_type = data['type']
            if data_type == 'initialization':
                await chatbot.send_initial_message(websocket)
            elif data_type == 'searching':
                await chatbot.process_user_input(data, websocket, credentials)
    except WebSocketDisconnect:
        await session.commit()
        await session.close()
