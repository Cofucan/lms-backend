from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from library.schemas.register import UserPublic


class LoginSchema(BaseModel):
    username_or_email: str
    password: str


class JWTSchema(BaseModel):
    user_id: str
    expire: Optional[datetime]


class AuthResponse(BaseModel):
    user: UserPublic
    token: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    password: str = Field(..., max_length=40, min_length=8)