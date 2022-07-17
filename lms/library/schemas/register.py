from pydantic import BaseModel, EmailStr, Field, root_validator
from library.dependencies.utils import regex
from uuid import UUID
import re


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=150)
    surname: str = Field(..., max_length=150)
    email: EmailStr
    password: str = Field(..., max_length=40, min_length=8)

    @root_validator()
    @classmethod
    def validate_password(cls, values):
        pwd = values.get("password")
        if not re.match(regex, pwd):
            raise ValueError(
                "Password must contain Min. 8 characters, 1 Uppercase,\
                1 lowercase, 1 number, and 1 special character"
            )
        return values


class UserPublic(BaseModel):
    id: UUID
    first_name: str = Field(..., max_length=50)
    surname: str = Field(..., max_length=50)
    email: EmailStr


class EmailVerify(BaseModel):
    email_verified: bool
