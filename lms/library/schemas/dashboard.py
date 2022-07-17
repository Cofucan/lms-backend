from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, root_validator
from library.schemas.enums import Stack, Track, Proficiency
from library.dependencies.utils import regex
from library.schemas.register import UserPublic


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


class ProfileUpdateSchema(BaseModel):
    stage: Optional[int]
    stack: Optional[Stack]
    track: Optional[Track]
    proficiency: Optional[Proficiency]
    old_password: Optional[str] = None
    password: Optional[str] = Field(regex=regex)