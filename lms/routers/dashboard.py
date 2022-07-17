from fastapi import APIRouter, status, Security, Path, HTTPException
from models.user import User
from models.dashboard import Announcement
from library.schemas.dashboard import (
    AnnouncementCreate as announce,
    AnnouncementResponse
    )
from library.dependencies.auth import get_current_user


router = APIRouter(prefix="/dashboard")


@router.post(
    "/announcements/",
    name="dashboard:announcements",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def announcements(
    data: announce,
    current_user=Security(get_current_user, scopes=["base"])
    ):
    if not current_user.is_admin:
        raise HTTPException(
            detail="Only admins can post an announcement",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    announcement = await Announcement.create(
            **data.dict(exclude_unset=True),
            creator=current_user
        )
    if not announcement:
        raise HTTPException(
            detail="Announcement create unsuccessful",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return AnnouncementResponse(
        creator=current_user, id=announcement.id,
        title=announcement.title, content=announcement.content
        )


@router.get(
    "/announcements/",
    name="dashboard:announcements",
    status_code=status.HTTP_200_OK,
)
async def get_announcements(
    current_user=Security(get_current_user, scopes=["base"])
):
    user = current_user
    general = await Announcement.filter(general="true")
    all_announcements = await Announcement.filter(
        stack=user.stack,
        stage=user.stage,
        track=user.track,
        proficiency=user.proficiency
        )
    if not (general or all_announcements):
        raise HTTPException(
            detail="Failed to load all announcements",
            status_code=status.HTTP_424_FAILED_DEPENDENCY
        )
    all_announcements.append(general)
    return all_announcements


@router.get(
    "/announcements/{announcement_id}",
    name="dashboard:announcements",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_200_OK,
)
async def get_announcements(
    announcement_id: str = Path(...),
    current_user=Security(get_current_user, scopes=["base"])
):
    announcement = await Announcement.get_or_none(id=announcement_id)
    creator = await User.get_or_none(id=announcement.creator_id)
    if not announcement:
        raise HTTPException(
            detail="Announcement not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return AnnouncementResponse(
        creator=creator, id=announcement.id,
        title=announcement.title, content=announcement.content
        )
  