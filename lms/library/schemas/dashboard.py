from typing import Optional
from pydantic import BaseModel, Field, root_validator

from library.dependencies.utils import regex, validate_stack_and_track
from library.schemas.register import UserPublic
from library.schemas.common import CommonBase, CommonResponse, SharedModel
from library.schemas.enums import Stack, Track, Proficiency


class AnnouncementCreate(BaseModel):
    title: str = Field(..., max_length=254, min_length=1)
    content: str = Field(..., max_length=654, min_length=1)
    general: bool
    stage: Optional[int] = Field(None, ge=0, le=10)
    stack: Optional[Stack]
    track: Optional[Track]
    proficiency: Optional[Proficiency]

    @root_validator()
    def validate_announcement(cls, values):
        stage = values.get("stage")
        stack = values.get("stack")
        track = values.get("track")
        general = values.get("general")
        proficiency = values.get("proficiency")
        if general and (stage or stack or track or proficiency):
            raise ValueError(
                "General cannot have a stack, stage, track or proficiency"
            )
        if not general and not stack:
            raise ValueError("General field cannot be false")
        return values

    @root_validator()
    def validate_input(cls, values):
        return validate_stack_and_track(values=values)

    @root_validator()
    def validate_fields(cls, values):
        stage = values.get("stage")
        track = values.get("track")
        proficiency = values.get("proficiency")
        if values.get("stack") and (not stage or not track or not proficiency):
            raise ValueError(
                "Stack announcement must have a stage, track and proficiency"
            )
        if (stage or track or proficiency) and not values.get("stack"):
            raise ValueError("Non-general announcement must have a stack")
        return values


class AnnouncementResponse(CommonResponse):
    creator: UserPublic


class LessonCreate(CommonBase):
    @root_validator()
    def validate_input(cls, values):
        return validate_stack_and_track(values=values)


class LessonResponse(CommonResponse):
    stack: str
    track: str
    proficiency: str
    stage: int


class PromoTaskCreate(CommonBase):
    deadline: int = Field(..., ge=1, le=14)

    @root_validator()
    def validate_input(cls, values):
        return validate_stack_and_track(values=values)


class ProfileUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, max_length=99)
    surname: Optional[str] = Field(None, max_length=99)
    phone: Optional[str] = Field(None, max_length=54)
    stack: Optional[Stack]
    track: Optional[Track]
    proficiency: Optional[Proficiency]
    old_password: Optional[str] = None
    password: Optional[str] = Field(regex=regex)

    @root_validator()
    def validate_password_values(cls, values):
        password = values.get("password")
        old_password = values.get("old_password")
        if old_password and not password:
            raise ValueError("Please new password must be provided")
        if password and not old_password:
            raise ValueError("Please old password must be provided")
        return values

    @root_validator()
    def validate_input(cls, values):
        return validate_stack_and_track(values=values)


class ResourceCreate(CommonBase):
    @root_validator()
    def validate_input(cls, values):
        return validate_stack_and_track(values=values)


class ResourceResponse(BaseModel):
    creator: UserPublic
    resources: ResourceCreate


class TaskSubmissionSchema(BaseModel):
    """Submit tasks"""

    url: str = Field(..., max_length=499)


class TaskPublicSchema(SharedModel):
    url: str
    graded: bool
    submitted: bool
