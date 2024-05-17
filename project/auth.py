import json

from starlette.responses import RedirectResponse
from fastapi import HTTPException, Request
from google.oauth2.credentials import Credentials
from fastapi.requests import Request
from googleapiclient.discovery import build
from sqlalchemy import select

from project.config import settings
from project.database import get_async_session
from project.users.models import User


async def get_current_user(request: Request) -> tuple | RedirectResponse:
    credentials_json = request.session.get('credentials')
    if not credentials_json:
        return RedirectResponse("/login")

    credentials_data = json.loads(credentials_json)
    credentials = Credentials.from_authorized_user_info(credentials_data)

    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            return RedirectResponse("/login")

    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info.get('email')
    if user_info is None or not email:
        raise HTTPException(status_code=401, detail="Unable to load user information")
    else:
        session = await get_async_session()
        user = await session.execute(select(User).where(User.email == email))
        user = user.scalars().one_or_none()
        if not user:
            user = User()
            user.email = email
            session.add(user)
            await session.commit()
        await session.close()
    return user, credentials
