from models.user import User
from fastapi import APIRouter, status, HTTPException, Security, Path
from routers.auth import pwd_context
from library.dependencies.auth import get_current_user
from library.dependencies.utils import get_queryset
from library.schemas.dashboard import (
    ProfileUpdateSchema,
    AnnouncementCreate as announce,
    AnnouncementResponse,
)
from models.dashboard import Announcement

router = APIRouter(prefix="/dashboard")


@router.put(
    "/user/profile/",
    status_code=status.HTTP_200_OK,
)
async def profile_update(
    data: ProfileUpdateSchema,
    current_user=Security(get_current_user, scopes=["base"]),
):
    """Handles user's profile update request

    Args:
        data - a pydantic schema that defines the user details to update
    Return:
        HTTP_200_OK response with a success message
    Raise:
        HTTP_424_FAILED_DEPENDENCY - if DB service fails to update profile
    """
    if data.old_password:
        password = data.password
        old_password = data.old_password

        verify_user_password: bool = pwd_context.verify(
            old_password, current_user.hashed_password
        )
        if not verify_user_password:
            raise HTTPException(
                detail="Incorrect password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        # Hash user's password before updating the User's data
        new_hashed_password = pwd_context.hash(password)
        await User.get(id=current_user.id).update(
            hashed_password=new_hashed_password
        )
    profile_updated = await User.get(id=current_user.id).update(
        **data.dict(exclude_unset=True, exclude={"password", "old_password"})
    )
    if not profile_updated:
        raise HTTPException(
            detail="Profile update unsuccessful",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return "Profile successfully updated"


@router.post(
    "/announcements/",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def announcements(
    data: announce,
    current_user=Security(get_current_user, scopes=["base", "root"]),
):
    """Handles announcement creation

    Args:
        data - a pydantic schema that defines announcement details
        current_user - retrieved from login auth
    Return:
        HTTP_201_CREATED response with pydantic serialized response data
    Raises:
        HTTP_401_UNAUTHORIZED if user is not admin
        HTTP_424_FAILED_DEPENDENCY if DB service fails create object
    """
    if not current_user.is_admin:
        raise HTTPException(
            detail="Only admins can post an announcement",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    announcement = await Announcement.create(
        **data.dict(exclude_unset=True), creator=current_user
    )
    if not announcement:
        raise HTTPException(
            detail="Announcement create unsuccessful",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return AnnouncementResponse(
        creator=current_user,
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        created_at=announcement.created_at,
    )


@router.get(
    "/announcements/",
    name="dashboard:all-announcements",
    status_code=status.HTTP_200_OK,
)
async def get_announcements(
    current_user=Security(get_current_user, scopes=["base"])
):
    """Gets all announcement using key fields in User object

    Args:
        current_user - retrieved from login auth
    Return:
        HTTP_200_OK response with a list of all related announcements
    Raises:
        HTTP_424_FAILED_DEPENDENCY if DB service fails retrieve objects
    """
    if current_user.is_admin:
        return await Announcement.all().order_by("-created_at")
    general = await Announcement.filter(general="true").order_by("-created_at")
    user_announcements = await Announcement.filter(
        **get_queryset(current_user)
    ).order_by("-created_at")
    user_announcements.append(general)
    try:
        len(user_announcements)
        return user_announcements
    except TypeError as e:
        raise HTTPException(
            detail="Failed to get all announcements",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        ) from e


@router.get(
    "/announcements/{announcement_id}",
    name="dashboard:announcement-id",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_200_OK,
)
async def get_announcement(
    announcement_id: str = Path(...),
    current_user=Security(get_current_user, scopes=["base"]),
):
    """Gets a single announcement by ID

    Args:
        announcement_id - path param retrieved from the URL
        current_user - retrieved from login auth
    Return:
        HTTP_200_OK response with retrieved announcement
    Raises:
        HTTP_404_NOT_FOUND if announcement object is not found
        HTTP_422_UNPROCESSABLE_ENTITY if announcement ID is invalid UUID type
    """
    try:
        announcement = await Announcement.get_or_none(id=announcement_id)
    except TypeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Announcement ID is an Invalid UUID type.",
        ) from e
    if not announcement:
        raise HTTPException(
            detail="Announcement not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    creator = await User.get_or_none(id=announcement.creator_id)
    if not creator:
        creator = None
    return AnnouncementResponse(
        creator=creator,
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        created_at=announcement.created_at,
    )
