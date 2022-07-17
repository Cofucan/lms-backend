from pydantic import BaseModel, Field
from typing import Optional

from datetime import datetime
from library.schemas.register import UserPublic
from library.schemas.shared import SharedModel
from library.schemas.common import CommonModel
from library.dependencies.utils import regex
import pydantic


class LessonCreate(BaseModel):
    title: str = Field(..., max_length=100)
    stack: str = Field(..., max_length=255)
    track: str = Field(..., max_length=100)
    proficiency: str = Field(..., max_length=100)
    stage: int = Field(..., ge=0, le=20)
    content: str = Field(..., max_length=655)


class LessonPublic(CommonModel):
    title: str
    stack: str
    track: str
    proficiency: str
    stage: int
    content: str


class PromoTaskCreate(BaseModel):
    title: str = Field(..., max_length=255)
    stack: str = Field(..., max_length=100)
    track: str = Field(..., max_length=255)
    proficiency: str = Field(..., max_length=100)
    stage: int = Field(..., ge=0, le=20)
    content: str = Field(..., max_length=655)
    active: bool
    feedback: Optional[str] = None
    deadline: Optional[datetime]


class PromoTaskPublic(CommonModel):
    title: str
    stack: str
    track: str
    proficiency: str
    stage: int
    content: str
    active: bool
    deadline: Optional[datetime]


class ProfileUpdateSchema(BaseModel):
    track: Optional[str] = None
    proficiency: Optional[str] = None
    old_password: Optional[str] = None
    password: Optional[str] = pydantic.Field(regex=regex)


class ResourceCreate(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., max_length=655)
    url: str = Field(..., max_length=500)
    filesize: str = Field(..., max_length=100)
    stack: str = Field(..., max_length=100)
    track: str = Field(..., max_length=255)
    proficiency: str = Field(..., max_length=100)


class ResourcePublic(BaseModel):
    creator: UserPublic
    resources: ResourceSchema


class TaskSubmissionSchema(BaseModel):
    """Submit tasks"""
    url: str = Field(..., max_length=500)


class TaskPublicSchema(SharedModel):
    url: str
    graded: bool
    submitted: bool
    resources: ResourceCreate
