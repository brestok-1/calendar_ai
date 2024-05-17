import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from project.database import engine

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI()

    from project.bot import bot_router
    app.include_router(bot_router, tags=['bot'])

    from project.users import user_router
    app.include_router(user_router, tags=['users'])

    from project.ws import ws_router
    app.include_router(ws_router, tags=['ws'])

    app.mount('/static', StaticFiles(directory="static"), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],

    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv('SECRET'),
        max_age=100
    )
    return app
