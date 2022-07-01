import json
import redis
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext
from library.security.otp import otp_manager
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
        
class TestLogin:
    async def test_login(
        self, app: FastAPI, client: AsyncClient, test_user
    ) -> None:
        request_data = {
            "username_or_email": test_user.email,
            "password": "@123Qwerty",
        }
        response = await client.post(
            app.url_path_for("auth:login"), json=request_data
        )
        assert response.status_code == 200
        res_data = response.json()

        assert "token" in res_data
        assert "user" in res_data

    # async def test_login_fails_on_incorrect_cred(
    #     self, app: FastAPI, client: AsyncClient, test_user
    # ) -> None:
    #     request_data = {
    #         "username_or_email": test_user.email,
    #         "password": "testingkjsdjrs456",
    #     }
    #     response = await client.post(
    #         app.url_path_for("auth:login"), json=request_data
    #     )
    #     assert response.status_code == 401
    #     assert (
    #         response.json().get("detail")
    #         == "Your authentication credentials is incorrect."
    #     )        
