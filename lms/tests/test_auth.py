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

        # Test successful registration with valid user data
        request_data_1 = {
            "first_name": "Alpha",
            "surname": "Test_first",
            "email": "test_email_alpha_bravo@kodecamp.com",
            "password": "testHGing-4567890",
        }
        response = await client.post(
            app.url_path_for("auth:register"), json=request_data_1
        )
        assert response.status_code == 201
        user = await User.get_or_none(email=request_data_1.get("email"))
        assert user is not None
        assert user.first_name == request_data_1.get("first_name")
        assert user.surname == request_data_1.get("surname")
        assert user.phone is None
        assert user.hashed_password != request_data_1.get("password")


        # Test for email already exists
        request_data_2 = {
            "first_name": "Bravo",
            "surname": "Test_second",
            "email": "test_email_alpha_bravo@kodecamp.com",
            "password": "AgxI=get/e357",
        }
        response = await client.post(
            app.url_path_for("auth:register"), json=request_data_2
        )
        assert response.status_code == 400


        # Test for weak password: no uppercase character
        request_data_3 = {
            "first_name": "Charlie",
            "surname": "Test_third",
            "email": "test_email_charlie@kodecamp.com",
            "password": ":r~]7s*tvc7/9g}?",
        }
        response = await client.post(
            app.url_path_for("auth:register"), json=request_data_3
        )
        assert response.status_code == 400


        # Test for weak password: no lowercase character
        request_data_4 = {
            "first_name": "Delta",
            "surname": "Test_fouth",
            "email": "test_email_delta@kodecamp.com",
            "password": "!J$5):^]ZK`=;${U",
        }
        response = await client.post(
            app.url_path_for("auth:register"), json=request_data_4
        )
        assert response.status_code == 400


        # Test for weak password: less than 8 characters
        request_data_5 = {
            "first_name": "Echo",
            "surname": "Test_fifth",
            "email": "test_email_echo@kodecamp.com",
            "password": "Pr=3-nS",
        }
        response = await client.post(
            app.url_path_for("auth:register"), json=request_data_5
        )
        assert response.status_code == 400


        # Test for weak password: no numeric character
        request_data_6 = {
            "first_name": "Fox",
            "surname": "Test_sixth",
            "email": "test_email_fox@kodecamp.com",
            "password": "UB.xd:HRT_Le",
        }
        response = await client.post(
            app.url_path_for("auth:register"), json=request_data_6
        )
        assert response.status_code == 400

        # # Test hashed password
        # hashed_password = user.hashed_password
        # is_valid_password: bool = pwd_context.verify(
        #     request_data_1.get("password"), hashed_password
        # )
        # assert is_valid_password

        # db = redis.Redis(host="redis", port=6379, db=1)
        # keys = db.keys()

        # assert len(keys) == 1


# class TestLogin:
#     async def test_login(
#         self, app: FastAPI, client: AsyncClient, test_user
#     ) -> None:
#         request_data = {
#             "username_or_email": test_user.email,
#             "password": "testing456",
#         }
#         response = await client.post(
#             app.url_path_for("auth:login"), json=request_data
#         )
#         assert response.status_code == 200
#         res_data = response.json()

#         assert "token" in res_data
#         assert "user" in res_data

#     async def test_login_fails_on_incorrect_cred(
#         self, app: FastAPI, client: AsyncClient, test_user
#     ) -> None:
#         request_data = {
#             "username_or_email": test_user.email,
#             "password": "testingkjsdjrs456",
#         }
#         response = await client.post(
#             app.url_path_for("auth:login"), json=request_data
#         )
#         assert response.status_code == 401
#         assert (
#             response.json().get("detail")
#             == "Your authentication credentials is incorrect."
#         )
