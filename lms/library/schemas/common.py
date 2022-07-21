from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from library.schemas.enums import Stack, Track, Proficiency


class CommonBase(BaseModel):
    """Shared pydantic data fields for schema

    Fields are required:
        title: str, content: str, stage: int

        Enum fields - stack: str, track: str, proficiency: str
    """

    title: str = Field(..., max_length=250, min_length=1)
    content: str = Field(..., max_length=654, min_length=1)
    stage: int = Field(..., ge=0, le=20)
    stack: Stack
    track: Track
    proficiency: Proficiency


class CommonResponse(BaseModel):
    """Shared pydantic response fields for schema

    Fields include:
        id: UUID, title: str, content: str, created_at: datetime
    """

    id: UUID
    title: str
    content: str
    created_at: datetime
