from models.user import User
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, HTTPException, Security, Path
from routers.auth import pwd_context
from library.dependencies.auth import get_current_user
from library.schemas.dashboard import (
    LessonCreate,
    LessonResponse,
    PromoTaskCreate,
    PromoTaskResponse,
    ResourceCreate,
    ResourceResponse,
    ProfileUpdateSchema,
    AnnouncementCreate as announce,
    AnnouncementResponse,
)
from models.dashboard import Lesson, PromotionTask, Resource, Announcement


router = APIRouter(prefix="/dashboard")


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
        return await Announcement.all()
    general = await Announcement.filter(general="true")
    user_announcements = await Announcement.filter(
        stack=current_user.stack,
        stage=current_user.stage,
        track=current_user.track,
        proficiency=current_user.proficiency,
    )
    try:
        len(general)
        return user_announcements.append(general)
    except TypeError as e:
        raise HTTPException(
            detail="Failed to get all promotional tasks",
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
    """
    announcement = await Announcement.get_or_none(id=announcement_id)
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


@router.post(
    "/lessons/",
    name="lesson:create",
    status_code=status.HTTP_201_CREATED,
    response_model=LessonResponse,
    description="Create lesson content.",
)
async def create_lesson(
    data: LessonCreate,
    current_user=Security(get_current_user, scopes=["base", "root"]),
):
    """Handles lesson(s) creation through a POST request

    Args:
        data - a pydantic schema that defines the required lesson(s) details
        current user - retrievd from login path
    Return:
        HTTP_201_CREATED response with a success message
    Raises:
        HTTP_401_UNAUTHORIZED if the current_user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only an admin can create lessons.",
        )

    lesson = await Lesson.create(
        **data.dict(exclude_unset=True), creator=current_user
    )
    if not lesson:
        raise HTTPException(
            detail="Lesson creation failed",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return lesson


@router.post(
    "/promotion-tasks/",
    name="dashboard:promotion-task",
    status_code=status.HTTP_201_CREATED,
    response_model=PromoTaskResponse,
    description="Create promotional task.",
)
async def create_promotion_task(
    data: PromoTaskCreate,
    current_user=Security(get_current_user, scopes=["base", "root"]),
):
    """Handles creation of promotional tasks

    Args:
        data - a pydantic schema that defines promotional task details
        current user - retrievd from login path
    Return:
        HTTP_201_CREATED response with a success message
    Raises:
        HTTP_401_UNAUTHORIZED if the current_user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only an admin can create promotional tasks.",
        )
    deadline = datetime.now(timezone.utc) + timedelta(days=data.deadline)
    promo_task = await PromotionTask.create(
        **data.dict(exclude_unset=True, exclude={"deadline"}),
        creator=current_user,
        deadline=deadline
    )
    if not promo_task:
        raise HTTPException(
            detail="Task creation failed",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return promo_task


@router.post(
    "/resources/",
    name="resource:create",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create resources.",
)
async def resource_create(
    data: ResourceCreate,
    current_user=Security(get_current_user, scopes=["base", "root"]),
):
    """Handles resource(s) post request

    Args:
        data - a pydantic schema that defines the resource(s) details
        current user - retrieved from login path
    Return:
        HTTP_201_CREATED response with a success message
    Raises:
        HTTP_401_UNAUTHORIZED if the current_user is n0t an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admin can create a resource",
        )
    resource_created = await Resource.create(
        **data.dict(exclude_unset=True), creator=current_user
    )
    if not resource_created:
        raise HTTPException(
            detail="Resource creation failed",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return {"resources": data, "creator": current_user}


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
    return {"message": "Profile successfully updated"}


@router.get(
    "/lessons/",
    name="dashboard:all-lessons",
    status_code=status.HTTP_200_OK,
)
async def get_lessons(
    current_user=Security(get_current_user, scopes=["base"])
):
    """Gets all lessons using key fields in User object

    Args:
        current_user - retrieved from login auth
    Return:
        HTTP_200_OK response with a list of all related lessons and their content
    Raises:
        HTTP_424_FAILED_DEPENDENCY if DB service fails retrieve objects
    """
    if current_user.is_admin:
        return await Lesson.all()
    user_lessons = await Lesson.filter(
        stack=current_user.stack,
        stage=current_user.stage,
        track=current_user.track,
        proficiency=current_user.proficiency,
    )
    try:
        len(user_lessons)
        return user_lessons
    except TypeError as e:
        raise HTTPException(
            detail="Failed to get all lessons",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        ) from e


@router.get(
    "/promotion-tasks/",
    name="dashboard:all-promotion-task",
    status_code=status.HTTP_200_OK,
)
async def get_promotion_tasks(
    current_user=Security(get_current_user, scopes=["base"])
):
    """Gets all promotional tasks using key fields in User object

    Args:
        current_user - retrieved from login auth
    Return:
        HTTP_200_OK response with a list of all promotional tasks and their content
    Raises:
        HTTP_424_FAILED_DEPENDENCY if DB service fails retrieve objects
    """
    if current_user.is_admin:
        return await PromotionTask.all()
    user_tasks = await PromotionTask.filter(
        stack=current_user.stack,
        stage=current_user.stage,
        track=current_user.track,
        proficiency=current_user.proficiency,
    )
    try:
        len(user_tasks)
        return user_tasks
    except TypeError as e:
        raise HTTPException(
            detail="Failed to get all promotional tasks",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        ) from e
