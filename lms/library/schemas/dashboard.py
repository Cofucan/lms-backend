from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, root_validator

from library.dependencies.utils import regex
from library.schemas.register import UserPublic
from library.schemas.common import CommonModel
from library.schemas.enums import Stack, Track, Proficiency

class AnnouncementCreate(BaseModel):
    title: str = Field(..., max_length=50, min_length=0)
    content: str = Field(..., max_length=654, min_length=0)
    general: bool
    stage: Optional[int]
    stack: Optional[Stack]
    track: Optional[Track]
    proficiency: Optional[Proficiency]

    @root_validator()
    def validate_announcement(cls, values):
        general = values.get("general")
        stage = values.get("stage")
        stack = values.get("stack")
        track = values.get("track")
        proficiency = values.get("proficiency")
        if general and (stage or stack or track or proficiency):
            raise ValueError(
                "General announcements cannot have a stack, stage, track or proficiency"
            )
        return values
    
    @root_validator()
    def validate_stack_and_track(cls, values):
        backend_tracks = ["nodejs", "python", "php", "golang"]
        frontend_tracks = ["vuejs", "reactjs", "vanillajs"]
        design_tracks = ["product design", "ui/ux design"]
        stack = values.get("stack")
        track = values.get("track")
        if values.get("general"):
            raise ValueError(
                "General field cannot be true for stack announcements"
            )
        if stack == "backend" and track not in backend_tracks:
            raise ValueError(
                "track selected is not a backend track"
            )
        if stack == "frontend" and track not in frontend_tracks:
            raise ValueError(
                "track selected is not a frontend track"
            )
        if stack == "design" and track not in design_tracks:
            raise ValueError(
                "track selected is not a design track"
            )
        return values


class AnnouncementResponse(BaseModel):
    title: str
    content: str
    id: UUID
    creator: UserPublic


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
    stack: Optional[Stack]
    track: Optional[Track]
    proficiency: Optional[Proficiency]
    old_password: Optional[str] = None
    password: Optional[str] = Field(regex=regex)


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
    resources: ResourceCreate
