from pydoc import Doc
import redis
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from passlib.context import CryptContext

from models.user import User

from essential_generators import DocumentGenerator
from library.dependencies.test_data import (
    generate_user, 
    generate_lesson, 
    generate_announcement
)

gen = DocumentGenerator()
pytestmark = pytest.mark.asyncio
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class TestAnnouncement:
#     user = generate_user()
#     announcement = generate_announcement(False)

#     # Test general announcement creation
#     async def test_announcement_general(
#         self, app: FastAPI, client: AsyncClient, test_user
#     ) -> None:





#         # Create announcement
#         response = await client.post(
#             app.url_path_for("dashboard:announcement"), json=self.announcement
#         )
#         assert response.status_code == 201

