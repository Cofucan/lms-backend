import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext

from models.user import User

from essential_generators import DocumentGenerator
from library.dependencies.test_data import (
    generate_user,
    generate_lesson,
    generate_announcement,
)

gen = DocumentGenerator()
pytestmark = pytest.mark.asyncio
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TestAnnouncement:
    user = generate_user()
    announcement = generate_announcement(True)

    # Test general announcement creation
    async def test_announcement_general(
        self, app: FastAPI, client: AsyncClient, test_user
    ) -> None:

        # Login admin
        admin_data = {
            "email": test_user.email,
            "password": "@123Qwerty",
        }
        response = await client.post(
            app.url_path_for("auth:login"), json=admin_data
        )
        assert response.status_code == 200

        admin_token = response.json().get("token")

        # Create announcement
        response = await client.post(
            app.url_path_for("announcements"),
            json=self.announcement,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201



"""
Unit Test To-Dos
- Test unauthorized accouncement creation
- Test user announcement creation
- Test multiple records in the database 100+ and assert data is all valid
    * users
    * announcements
    * lessons
    * promotional tasks
    * notifications
"""
