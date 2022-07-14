from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, root_validator, Field

from library.schemas.register import UserPublic
from library.schemas.register import UserPublic, regex
import re


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class JWTSchema(BaseModel):
    user_id: str
    expire: Optional[datetime]


class AuthResponse(BaseModel):
    user: UserPublic
    token: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class PasswordResetSchema(BaseModel):
    password: str = Field(..., max_length=40, min_length=8, regex=regex)
    confirm_password: str

    @root_validator()
    def verify_password_match(cls, values):
        password = values.get("password")
        confirm_password = values.get("confirm_password")

        if password != confirm_password:
            raise ValueError("The two passwords did not match.")
        return values
