import redis
import pytest
import asyncio
from jose import jwt
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext
from asgi_lifespan import LifespanManager
from datetime import datetime, timezone, timedelta
from tortoise.contrib.fastapi import register_tortoise

from models.user import User
from server import get_application
from library.schemas.auth import JWTSchema
from config import DATABASE_URL, SECRET_KEY, ALGORITHM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="module")
def app() -> FastAPI:
    """Get a reference to the application."""
    app = get_application()
    return app


@pytest.fixture(scope="class")
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        ) as client:
            yield client


@pytest.fixture(scope="module", autouse=True)
async def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=DATABASE_URL,
        modules={
            "models": [
                "models",
                "aerich.models",
            ]
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="class", autouse=True)
async def clean_database():
    yield
    await User.all().delete()


@pytest.fixture(autouse=True)
def clean_redis():
    r = redis.Redis(host="redis", port=6379)
    r.flushall()


@pytest.fixture()
async def test_user():
    user_password = "@123Qwerty"
    hashed_password = pwd_context.hash(user_password)
    email = "test@email.com"

    email_exists = await User.filter(email=email).exists()

    if email_exists:
        return await User.get(email=email)
    else:
        return await User.create(
            email="test@email.com",
            first_name="Test",
            surname="User",
            email_verified=True,
            hashed_password=hashed_password,
        )


@pytest.fixture()
def authorized_client(client: AsyncClient, test_user) -> AsyncClient:
    """Create authorized client."""
    jwt_data = JWTSchema(user_id=str(test_user.id))
    to_encode = jwt_data.dict()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"expire": str(expire)})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {encoded_jwt}",
    }
    return client
