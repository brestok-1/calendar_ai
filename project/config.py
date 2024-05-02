import os
import pathlib
from functools import lru_cache
from environs import Env

from openai import AsyncOpenAI

env = Env()
env.read_env()


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    OPENAI_CLIENT = AsyncOpenAI(api_key=env('OPENAI_API_KEY'))
    DATABASE_URL = f"postgresql+asyncpg://{env('DATABASE_USER')}:" \
                   f"{env('DATABASE_PASSWORD')}@" \
                   f"{env('DATABASE_HOST')}:" \
                   f"{env('DATABASE_PORT')}/" \
                   f"{env('DATABASE_NAME')}"
    GOOGLE_CALENDAR_PROMPT = "You are virtual assistant in Google Calendar, You are here to help user manage and " \
                             "navigate their events seamlessly. User can ask you to display all upcoming events, " \
                             "add a new event, or predict the next event on your calendar. Whenever user make a " \
                             "request, you will acknowledge it with a positive and polite confirmation. "


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    ORIGINS = [
        "http://localhost:3000",
    ]


class TestConfig(BaseConfig):
    pass


@lru_cache()
def get_settings() -> DevelopmentConfig | ProductionConfig | TestConfig:
    config_cls_dict = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestConfig
    }
    config_name = env('FASTAPI_CONFIG', default='production')
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
