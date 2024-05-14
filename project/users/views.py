import os

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from starlette.responses import RedirectResponse

from fastapi import Request, HTTPException

from . import user_router
from ..config import settings


@user_router.get("/login")
async def login():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    flow = Flow.from_client_secrets_file(
        str(settings.BASE_DIR / 'credentials.json'),
        scopes=settings.SCOPES,
        redirect_uri="http://localhost:8000/auth/"
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)


@user_router.get("/auth")
async def auth(request: Request):
    flow = Flow.from_client_secrets_file(
        str(settings.BASE_DIR / 'credentials.json'),
        scopes=settings.SCOPES,
        redirect_uri="http://localhost:8000/auth/"
    )
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials
    request.session['credentials'] = creds.to_json()
    return RedirectResponse('/')
