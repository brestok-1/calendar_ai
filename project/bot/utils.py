from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from project.bot.models import Message


async def update_message_history(role: str, content: str, chat_id: int, session: AsyncSession) -> None:
    message = Message()
    message.role = role
    message.content = content
    message.chat_id = int(chat_id)
    session.add(message)
    await session.commit()


def format_datetime(iso_str):
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime('%Y-%m-%d %H:%M')


async def collect_all_events_from_past_year():
    pass
