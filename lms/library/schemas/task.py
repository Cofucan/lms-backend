from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class TaskSubmit(BaseModel):
    """Submit tasks"""
    url: str = Field(..., max_length=500)