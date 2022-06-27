from email.policy import default
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4



class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=150)
    surname: str = Field(..., max_length=150)
    email: EmailStr
    password: str = Field(..., max_length=40, min_length=8)


class UserPublic(BaseModel):
    id: UUID
    first_name: str = Field(..., max_length=50)
    surname: str = Field(..., max_length=50)
    email: EmailStr
       

class EmailVerify(BaseModel):
    email_verified: bool