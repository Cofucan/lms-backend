from pydantic import BaseModel, EmailStr, Field, root_validator
from library.dependencies.utils import validate_password
from uuid import UUID


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=150)
    surname: str = Field(..., max_length=150)
    email: EmailStr
    password: str = Field(..., max_length=40, min_length=8)

    @root_validator()
    def validate_password_value(cls, values):
        return validate_password(values=values)


class UserPublic(BaseModel):
    id: UUID
    first_name: str = Field(..., max_length=50)
    surname: str = Field(..., max_length=50)
    is_admin: bool


class EmailVerify(BaseModel):
    email_verified: bool
