from routers.auth import router, pwd_context
from models.user import User
from models.dashboard import Resource 
from fastapi import status, HTTPException, Security
from models.user import User
from models.dashboard import (
    Resource, 
    TaskSubmission,
    PromotionTask
)
from library.dependencies.auth import get_current_user
from library.schemas.dashboard import (
    ResourceSchema,
    ResourcePublicSchema,
    ProfileUpdateSchema,
    TaskSubmissionSchema,
    TaskPublicSchema
)


@router.post(
    "/resource/post/",
    response_model=ResourcePublicSchema,
    status_code=status.HTTP_201_CREATED,
)
async def resources_create(
    data: ResourceSchema,
    current_user=Security(get_current_user, scopes=["base", "root"]),
):
    """Handles resource(s) post request

    Args:
        data - a pydantic schema that defines the required resouce(s) details
        current user - a Dependency that extract user's token from the login url
    Return:
        HTTP_201_CREATED response with a success message
    Raises:
        HTTP_401_UNAUTHORIZED if the user trying to create resource(s) isn't an admin
    """
    verify_user = await User.get(id=current_user.id)
    if verify_user.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admin can create a resource",
        )
    await Resource.create(**data.dict(exclude_unset=True), creator=verify_user)
    context = {"resources": data, "creator": verify_user}
    return context


@router.put("/user/profile-update/", status_code=status.HTTP_200_OK)
async def profile_update(
    data: ProfileUpdateSchema,
    current_user=Security(get_current_user, scopes=["base", "roots"]),
):

    """Handles user's profile update request

    Args:
        data - a pydantic schema that defines the required user's details to be updated
    Return:
        HTTP_200_OK response with a success message
    Raise:
        HTTP_404_NOT_FOUND - throws a does not exist error if there's no user with the supplied token
        HTTP_400_BAD_REQUEST- throws an error if new password isn't supplied for password update
        HTTP_400_BAD_REQUEST- throws an error if old password isn't supplied for password update
        HTTP_400_BAD_REQUEST- throws an error if password supplied does not match
    """
    user = await User.get(id=current_user.id)
    if not user:
        raise HTTPException(
            detail="User does not exist", status_code=status.HTTP_404_NOT_FOUND
        )
    user_hashed_password = user.hashed_password
    password = data.password
    old_password = data.old_password
    if not password and not old_password:
        # Updates user profile based on request data if password isn't provided
        await User.get(id=current_user.id).update(
            **data.dict(exclude_unset=True)
        )
        return "Profile update was successful"
        # Verify if old password data is provided without the new password data
    if old_password and not password:
        return ValueError({"error": "Provide new password"})
    # return error if old password isn't provided it's a 'Profile update' endpoint and not 'Forget Password'
    if not old_password:
        raise HTTPException(
            detail={"error": "Old password must be provided"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    # Verify is the supplied old password correlates with the User's hashed password in the database
    verify_user_password: bool = pwd_context.verify(
        old_password, user_hashed_password
    )
    # Throw an error if the supplied password password does not match
    if not verify_user_password:
        raise HTTPException(
            detail={"error": "Incorrect password"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    # Hash user's password before updating the User's data
    hashed_password = pwd_context.hash(data.password)
    updated_user = await User.get(id=current_user.id).update(
        **data.dict(exclude_unset=True, exclude={"password", "old_password"}),
        hashed_password=hashed_password,
    )
    return "Profile Update successfully"



@router.post(
    "/submit-task/{task_id}/",
    name="task:submit",
    status_code=status.HTTP_200_OK,
    response_model=TaskPublicSchema,
    description="Submit a task."    
)
async def submit_task(
    data:TaskSubmissionSchema,
    task: str = Path(...),
    current_user = Security(get_current_user, scopes=["base", "root"])
):
    task = await PromotionTask.get_or_none(id=task_id) 
    submission = await TaskSubmission.create(
        url=data.url,
    ) 
