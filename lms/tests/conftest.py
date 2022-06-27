import pytest
import redis
from fastapi import FastAPI
from asgi_lifespan import LifespanManager
from httpx import AsyncClienct
from tortoise.contrib.fastapi import register_tortoise

from server import get_application
from config import DATABASE_URL
 

@pytest.fixture(scope="module")
def app() -> FastAPI:
    "Get a reference to the applicaton"
    app = get_application()
    return app

