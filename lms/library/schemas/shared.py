from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class SharedModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime | None