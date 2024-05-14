import asyncio
from datetime import datetime

from fastapi import Depends
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from project.auth import get_current_user
from project.bot import bot_router
from project.bot.calendar_apis import add_new_event, show_events, delete_event
from project.bot.models import Message, Chat
from project.bot.openai_requests import analyze_request_type, generate_ai_response
from project.bot.schemas import UserMessageRequestSchema, GeneratedAnswerSchema
from project.bot.utils import update_message_history
from project.database import get_async_session

template = Jinja2Templates(directory='project/bot/templates')


@bot_router.get('/', name='main')
async def main(request: Request):
    return template.TemplateResponse("home.html", {'request': request})


@bot_router.post("/message/create")
async def generate_message(data: UserMessageRequestSchema, user_data=Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)) -> GeneratedAnswerSchema:
    chat_messages = await session.execute(select(Message).where(Message.chat_id == data.chat_id))
    chat_messages = chat_messages.scalars().all()
    message_history = [{'role': message.role, "content": message.content} for message in chat_messages]
    message_history += [{'role': 'user', 'content': data.query}]

    today = datetime.utcnow().isoformat() + "Z"
    request_data = await analyze_request_type(message_history, today)
    credentials = user_data[1]

    events_str = ''
    if request_data['type'] == 'add':
        await add_new_event(request_data, credentials, data.timezone)
    elif request_data['type'] == 'show':
        events_str = await show_events(request_data, credentials)
    elif request_data["type"] == 'delete':
        await delete_event(request_data, credentials)
    # elif request_data["type"] == 'predict':
    #     await predict_new_event(request_data, credentials, today)
    response = await generate_ai_response(message_history)

    assistant_message_schema = GeneratedAnswerSchema(
        response=response + f'\n{events_str}',
    )
    await update_message_history('user', data.query, data.chat_id, session)
    await update_message_history('assistant', assistant_message_schema.response, data.chat_id, session)
    return assistant_message_schema


@bot_router.get('/chat/create')
async def create_new_chat(user_data=Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    if isinstance(user_data, RedirectResponse):
        return user_data

    chat_object = Chat()
    chat_object.user_id = user_data[0].id
    session.add(chat_object)
    await session.commit()
    await session.refresh(chat_object)
    return {'chat_id': chat_object.id}


@bot_router.get('/message/history/{chat_id}')
async def get_message_history(chat_id: str, user_data=Depends(get_current_user),
                              session: AsyncSession = Depends(get_async_session)):
    chat_messages = await session.execute(select(Message).where(Message.chat_id == int(chat_id)))
    chat_messages = chat_messages.scalars().all()
    return chat_messages
