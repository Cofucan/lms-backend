from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator

from library.schemas.common import CommonModel


class LessonCreate(BaseModel):
    title: str = Field(..., max_length=100)
    stack: str = Field(..., max_length=255)
    track: str = Field(..., max_length=100)
    stage: int = Field(..., ge=0, le=20)
    content: str = Field(..., max_length=655)

class LessonPublic(CommonModel):
    title: str
    stack: str
    track: str
    stage: str
    content: str
    # proficiency: str