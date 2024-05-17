import ast
import json

from fastapi import Depends
from google.oauth2.credentials import Credentials
from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect

from . import ws_router
from .bots import PredictionBot
from ..auth import get_current_user
from ..database import get_async_session


@ws_router.websocket("/ws/prediction/{timezone1}/{timezone2}")
async def search_products_test(websocket: WebSocket, timezone1: str, timezone2: str):
    await websocket.accept()
    timezone = f'{timezone1}/{timezone2}'
    chatbot = PredictionBot(timezone)
    # user, credentials = await get_current_user(request)
    session = await get_async_session()
    credentials = None
    try:
        while True:
            data = await websocket.receive_json()
            data_type = data['type']
            if data_type == 'initialization':
                credentials = data['credentials'].replace('\n', '').strip()
                credentials_data = ast.literal_eval(credentials)
                # credentials_data = json.loads(credentials)
                credentials = Credentials.from_authorized_user_info(credentials_data)
                await chatbot.send_initial_message(websocket)
            elif data_type == 'searching':
                await chatbot.process_user_input(data, websocket, credentials)
    except WebSocketDisconnect:
        await session.commit()
        await session.close()
