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


    # async def test_email_verify(self, app: FastAPI, client: AsyncClient) -> None:
    #     request_data = {
    #         "first_name": "Hello",
    #         "surname": "test_username",
    #         "email": "tester_email@kodecamp.com",
    #         "password": "testHGing-4567890",
    #     }
    #     response = await client.post(
    #         app.url_path_for("auth:register"), json=request_data
    #     )
    #     print(response.json())
    #     otp = response.json().get("token")
        
    #     print("1=",otp)
    #     verify_email_response = await client.put(
    #         app.url_path_for("email_verification", otp=otp)
    #     )
    #     # verify_otp = await otp_manager.get_otp_user(otp)
    #     # assert verify_email_response.detail != "OTP is invalid or expired"
    #     assert verify_email_response.status_code ==200
    #     assert verify_email_response.status_code !=401
