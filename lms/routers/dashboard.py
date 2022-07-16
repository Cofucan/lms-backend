from typing import List

from fastapi import APIRouter, status, Security, Path, Depends, HTTPException

from library.schemas.dashboard import (
    LessonCreate,
    LessonPublic
)
from library.dependencies.auth import get_current_user
from models.user import User
from models.dashboard import Lesson
from library.dependencies.utils import *


router = APIRouter(prefix="/dashboard")

@router.post(
    "/create-lesson/",
    # name="course:create",
    status_code=status.HTTP_201_CREATED,
    response_model=LessonPublic,
    # description="Create course content.",
)
async def create_lesson(
    data: LessonCreate, 
    current_user=Security(get_current_user, scopes=["base"])
):
    user = await User.get(id=current_user.id)
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only an admin can create lessons."
        )

    lesson = await Lesson.create(
        **data.dict(exclude_unset=True), creator=current_user)

    return lesson