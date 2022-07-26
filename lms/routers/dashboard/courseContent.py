from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, HTTPException, Security, Path
from library.dependencies.auth import get_current_user
from library.dependencies.utils import get_queryset
from library.schemas.dashboard import (
    LessonCreate,
    LessonResponse,
    PromoTaskCreate,
    ResourceCreate,
    ResourceResponse,
    TaskSubmissionSchema,
    TaskPublicSchema,
)
from models.dashboard import Lesson, PromotionTask, Resource, TaskSubmission

router = APIRouter(prefix="/dashboard")


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
        HTTP_200_OK response with a list of all related lessons
    Raises:
        HTTP_424_FAILED_DEPENDENCY if DB service fails retrieve objects
    """
    if current_user.is_admin:
        return await Lesson.all().order_by("-created_at")
    user_lessons = await Lesson.filter(**get_queryset(current_user)).order_by(
        "-created_at"
    )
    try:
        len(user_lessons)
        return user_lessons
    except TypeError as e:
        raise HTTPException(
            detail="Failed to get all lessons",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        ) from e


@router.post(
    "/promotion-tasks/",
    name="dashboard:promotion-task",
    status_code=status.HTTP_201_CREATED,
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
        active=True,
        deadline=deadline
    )
    if not promo_task:
        raise HTTPException(
            detail="Task creation failed",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return promo_task


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
        HTTP_200_OK response with a list of all promotional tasks
    Raises:
        HTTP_424_FAILED_DEPENDENCY if DB service fails retrieve objects
    """
    if current_user.is_admin:
        return await PromotionTask.all().order_by("-created_at")
    user_tasks = await PromotionTask.filter(
        **get_queryset(current_user)
    ).order_by("-created_at")
    try:
        len(user_tasks)
        return user_tasks
    except TypeError as e:
        raise HTTPException(
            detail="Failed to get all promotional tasks",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        ) from e


@router.get(
    "/promotion-tasks/{task_id}",
    name="dashboard:all-promotion-task",
    status_code=status.HTTP_200_OK,
)
async def get_promotion_task(
    task_id: str = Path(...),
    current_user=Security(get_current_user, scopes=["base"]),
):
    """Gets a promotional task by id

    Args:
        current_user - retrieved from login auth
    Return:
        HTTP_200_OK response with the task object
    Raises:
        HTTP_424_FAILED_DEPENDENCY if DB service fails retrieve task
        HTTP_422_UNPROCESSABLE_ENTITY if task ID is invalid UUID type
    """
    try:
        task = await PromotionTask.get_or_none(id=task_id)
    except TypeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task ID is an Invalid UUID type.",
        ) from e
    if not task:
        raise HTTPException(
            detail="Failed to get task",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return task


@router.post(
    "/submit-task/{task_id}/",
    name="task:submit",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskPublicSchema,
    description="Submit a task.",
)
async def submit_task(
    data: TaskSubmissionSchema,
    task_id: str = Path(...),
    current_user=Security(get_current_user, scopes=["base", "root"]),
):
    """
    Handles user task submissions,

    Args:
        data - A pydantic schema that defines the task url to be submitted.
        task_id - The task id for which a task is to be submitted.
        current_user - Retrieved from login path.

    Return:
        HTTP_201_CREATED when a submission is made (created)

    Raise:
        HTTP_404_NOT_FOUND task not found
        HTTP_422_UNPROCESSABLE_ENTITY if task ID is invalid UUID type
        HTTP_409_CONFLICT task deadline has elapsed or no longer active.
    """
    try:
        task = await PromotionTask.get_or_none(id=task_id)
    except TypeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task ID is an Invalid UUID type.",
        ) from e
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promotional task not found",
        )
    # check to know if promotional task  is still active
    if str(task.deadline) < str(datetime.now()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task deadline has elapsed.",
        )
    if task.active is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Promotional task is not active",
        )
    submission = await TaskSubmission.create(
        user=current_user, task=task, url=data.url, submitted=True
    )
    return submission


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


@router.get(
    "/resources/",
    name="resource:get",
    status_code=status.HTTP_200_OK,
)
async def resource(
    current_user=Security(get_current_user, scopes=["base"]),
):
    # return all resources if user is an admin
    if current_user.is_admin:
        return await Resource.all().order_by("-created_at")
    user_resources = await Resource.filter(
        **get_queryset(current_user)
    ).order_by("-created_at")
    try:
        len(user_resources)
        return user_resources
    except TypeError as e:
        raise HTTPException(
            detail="Failed to get all user resources",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        ) from e
