from pydantic import BaseModel, Field
from typing import Optional
from library.schemas.register import UserPublic
from library.schemas.shared import SharedModel
from library.dependencies.utils import regex
import pydantic


class ProfileUpdateSchema(BaseModel):
    track: Optional[str] = None
    proficiency: Optional[str] = None
    old_password: Optional[str] = None
    password: Optional[str] = pydantic.Field(regex=regex)


class ResourceSchema(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., max_length=655)
    url: str = Field(..., max_length=500)
    filesize: str = Field(..., max_length=100)
    stack: str = Field(..., max_length=100)
    track: str = Field(..., max_length=255)
    proficiency: str = Field(..., max_length=100)


class ResourcePublicSchema(BaseModel):
    creator: UserPublic
    resources: ResourceSchema


class TaskSubmissionSchema(BaseModel):
    """Submit tasks"""
    url: str = Field(..., max_length=500)


class TaskPublicSchema(SharedModel):
    url: str
    graded: bool
    submitted: bool
