import redis
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext

from models.user import User


pytestmark = pytest.mark.asyncio
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestRegister:
    request_data = {
        "first_name": "Alpha",
        "surname": "Test_first",
        "email": "test_email_alpha_bravo@kodecamp.com",
        "password": "testHGing-4567890",
        }

    # Test successful registration with valid user data
    async def test_register_valid_user(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 201
        user = await User.get_or_none(email=self.request_data.get("email"))
        assert user is not None
        assert user.first_name == self.request_data.get("first_name")
        assert user.surname == self.request_data.get("surname")
        assert user.phone is None
        assert user.hashed_password != self.request_data.get("password")

        user = await User.get_or_none(email=self.request_data.get("email"))
        hashed_password = user.hashed_password
        is_valid_password: bool = pwd_context.verify(
            self.request_data.get("password"), hashed_password
        )
        assert is_valid_password

        db = redis.Redis(host="redis", port=6379, db=1)
        keys = db.keys()

        assert len(keys) == 1


    # Test for email already exists
    async def test_register_user_exists(self, app: FastAPI, client: AsyncClient) -> None:
        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 400
        assert (
            response.json().get("detail")
            == "User with this email already exist"
        )


    # Test for weak password: no uppercase character
    async def test_register_password_no_upper(self, app: FastAPI, client: AsyncClient) -> None:
        self.request_data["password"] = ":r~]7s*tvc7/9g}?"

        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 400
        assert (
                response.json().get("detail")
            ==  {
                "password": "Your Password Is Weak",
                "Hint": "Min. 8 characters, 1 Uppercase, 1 lowercase, 1 number, and 1 special character",
            },
        )

    # Test for weak password: no lowercase character
    async def test_register_password_no_lower(self, app: FastAPI, client: AsyncClient) -> None:
        self.request_data["password"] = "!J$5):^]ZK`=;${U"

        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 400


    # Test for weak password: no numeric character
    async def test_register_password_no_nummber(self, app: FastAPI, client: AsyncClient) -> None:
        self.request_data["password"] = "UB.xd:HRT_Le"

        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 400
        assert (
                response.json().get("detail")
            ==  {
                "password": "Your Password Is Weak",
                "Hint": "Min. 8 characters, 1 Uppercase, 1 lowercase, 1 number, and 1 special character",
            },
        )

    # Test for email exists: case-sensitive
    async def test_register_user_exists_case_sensitive(self, app: FastAPI, client: AsyncClient) -> None:
        self.request_data["email"] = "test_email_fox@kodecamp.com"
        self.request_data["password"] = "UB.xd:61RT_Le"
        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 201


        self.request_data["email"] = "test_email_FOX@kodecamp.com"
        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 400
        assert (
            response.json().get("detail")
            == "User with this email already exist"
        )



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

    async def test_login_fails_on_incorrect_cred(
        self, app: FastAPI, client: AsyncClient, test_user
    ) -> None:
        request_data = {
            "username_or_email": test_user.email,
            "password": "testingkjsdjrs456",
        }
        response = await client.post(
            app.url_path_for("auth:login"), json=request_data
        )
        assert response.status_code == 401
        assert (
            response.json().get("detail")
            == "Password Incorrect"
        )
