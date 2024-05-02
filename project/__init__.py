from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from project.database import engine


def create_app() -> FastAPI:
    app = FastAPI()

    from project.bot import bot_router
    app.include_router(bot_router, tags=['bot'])

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

    return app
