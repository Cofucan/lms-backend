from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, root_validator, Field

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


class ProfileUpdateSchema(BaseModel):
    track: Optional[str] = None
    proficiency: Optional[str] = None
    old_password: Optional[str] =None
    password: Optional[str] =None

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

class ResourceSchema(BaseModel):
    title: str = Field(..., max_length=255)
    content:str = Field(..., max_length=655)
    url:str = Field(..., max_length=500)
    filesize:str = Field(..., max_length=100)
    stack:str = Field(..., max_length=100)
    track:str = Field(..., max_length=255)
    proficiency:str = Field(..., max_length=100)



class ResourcePublicSchema(BaseModel):
    creator: UserPublic
    resources: ResourceSchema