import redis
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext

from models.user import User


pytestmark = pytest.mark.asyncio
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestRegister:
    async def test_register(self, app: FastAPI, client: AsyncClient) -> None:
        request_data = {
            "first_name": "Hello",
            "surname": "test_username",
            "email": "test_email@kodecamp.com",
            "password": "testHGing-4567890",
        }
        response = await client.post(
            app.url_path_for("auth:register"), json=request_data
        )
        assert response.status_code == 201
        user = await User.get_or_none(email=request_data.get("email"))
        assert user is not None
        assert user.first_name == request_data.get("first_name")
        assert user.surname == request_data.get("surname")
        assert user.phone is None
        assert user.hashed_password != request_data.get("password")

        hashed_password = user.hashed_password
        is_valid_password: bool = pwd_context.verify(
            request_data.get("password"), hashed_password
        )
        assert is_valid_password

        db = redis.Redis(host="redis", port=6379, db=1)
        keys = db.keys()

        assert len(keys) == 1