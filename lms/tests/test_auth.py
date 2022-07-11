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
        "surname": "Bravo",
        "email": "test_email_alpha_bravo@kodecamp.com",
        "password": "testHGing@4567890",
    }

    # Test successful registration with valid user data
    async def test_register_valid_user(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
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
    async def test_register_user_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 400
        assert (
            response.json().get("detail")
            == "User with this email already exist"
        )

    # Test for weak password: no uppercase character
    async def test_register_password_no_upper(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        self.request_data["password"] = "#1password"

        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 422

    # Test for weak password: no lowercase character
    async def test_register_password_no_lower(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        self.request_data["password"] = "#1PASSWORD"

        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 422

    # Test for weak password: no numeric character
    async def test_register_password_no_nummber(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        self.request_data["password"] = "#Password"

        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 422

    # Test for email exists: case-sensitive
    async def test_register_user_exists_case_sensitive(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        self.request_data["email"] = "test_email_Alpha_Bravo@kodecamp.com"
        self.request_data["password"] = "#1Password"
        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        assert response.status_code == 400
        assert (
            response.json().get("detail")
            == "User with this email already exist"
        )

    async def test_email_verification(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        self.request_data["email"] = "tester_email@kodecamp.com"
        self.request_data["password"] = "#123Password"
        response = await client.post(
            app.url_path_for("auth:register"), json=self.request_data
        )
        otp = response.json().get("token")
        email_verify_response = await client.put(
            app.url_path_for("email_verification", otp=otp)
        )
        assert email_verify_response.status_code == 200
        assert email_verify_response.status_code != 401


class TestLogin:
    async def test_login(
        self, app: FastAPI, client: AsyncClient, test_user
    ) -> None:
        request_data = {
            "email": test_user.email,
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
            "email": test_user.email,
            "password": "testingkjsdjrs456",
        }
        response = await client.post(
            app.url_path_for("auth:login"), json=request_data
        )
        assert response.status_code == 401
        assert (
            response.json().get("detail")
            == "Your email or password is incorrect."
        )

    async def test_forgot_password(
        self, app: FastAPI, client: AsyncClient, test_user
    ) -> None:
        req_data = {"email": test_user.email}
        response = await client.post(
            app.url_path_for("auth:forgot-password"), json=req_data
        )
        assert response.status_code == 200
        assert (
            response.json().get("message")
            == f"Password reset link sent to {test_user.email}"
        )

    async def test_password_reset(
        self, app: FastAPI, client: AsyncClient, test_user
    ) -> None:
        req_data = {
            "password": "#123Qwertyz",
            "confirm_password": "#123Qwertyz",
        }
        response = await client.post(
            app.url_path_for("auth:forgot-password"),
            json={"email": test_user.email},
        )
        token = response.json().get("token")
        response = await client.put(
            app.url_path_for("password_reset", token=token), json=req_data
        )
        assert response.status_code == 200
        assert response.json().get("message") == "Password reset successful"
