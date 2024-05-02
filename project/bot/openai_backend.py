import asyncio
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from project.bot.models import Message
from project.config import settings


class SearchBot:
    chat_history = []

    # is_unknown = False
    # unknown_counter = 0

    def __init__(self, memory=None):
        if memory is None:
            memory = []
        self.chat_history = memory

    @staticmethod
    def _cls_pooling(model_output):
        return model_output.last_hidden_state[:, 0]

    async def _rag(self, query: str, session: AsyncSession):
        user_message = {"role": 'user', "content": query}
        self.chat_history.append(user_message)
        session.add(Message(role='user', content=query))
        messages = [
            {
                'role': 'system',
                'content': settings.GOOGLE_CALENDAR_PROMPT
            },
        ]
        messages = messages + self.chat_history

        stream = await settings.OPENAI_CLIENT.chat.completions.create(
            messages=messages,
            temperature=0.1,
            n=1,
            model="gpt-3.5-turbo",
            stream=True
        )
        response = ''
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                chunk_content = chunk.choices[0].delta.content
                response += chunk_content
                yield response
                await asyncio.sleep(0.02)
        assistant_message = {"role": 'assistant', "content": response}
        self.chat_history.append(assistant_message)
        try:
            session.add(Message(role='assistant', content=response))
        except Exception as e:
            print(e)

    async def ask_and_send(self, data: Dict, websocket: WebSocket, session: AsyncSession):
        query = data['query']
        try:
            async for chunk in self._rag(query, session):
                await websocket.send_text(chunk)
        except Exception as e:
            print(e)
            await self.emergency_db_saving(session)

    @staticmethod
    async def emergency_db_saving(session: AsyncSession):
        await session.commit()
        await session.close()
