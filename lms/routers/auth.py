# Libraries
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, Path, HTTPException, Security

# Files, Models, Schemas, Dependencies
from models.user import User
from library.security.otp import otp_manager
from library.dependencies.utils import to_lower_case
from library.dependencies.auth import get_current_user
from library.schemas.register import UserCreate, EmailVerify, UserPublic
from library.schemas.auth import (
    LoginSchema,
    AuthResponse,
    JWTSchema,
    PasswordResetSchema,
    ForgotPasswordSchema,
)
from config import SECRET_KEY, ALGORITHM


router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post(
    "/register/",
    response_model=UserPublic,
    name="auth:register",
    status_code=status.HTTP_201_CREATED,
)
async def register(data: UserCreate):
    """Creates a new user

    Registers a user in the database
    Returns user details when successfully registered
    Args:
        data - a pydantic schema that defines the user registration params
    Returns:
        HTTP_201_CREATED (with user details as defined in the response model)
        Sends otp via SMTP as a background task
    Raises:
        HTTP_400_BAD_REQUEST if user exists or weak password
    """

    # Converts user email to lower-case
    valid_email = to_lower_case(data.email)

    email_exist = await User.exists(email=valid_email)
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )

    hashed_password = pwd_context.hash(data.password)

    created_user = await User.create(
        **data.dict(exclude_unset=True, exclude={"password"}),
        hashed_password=hashed_password,
        stage=0,
    )
    otp = otp_manager.create_otp(user_id=str(created_user.id))
    # pending - send otp as background task to registered email
    return created_user


@router.put(
    "/set-permission/{email}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def set_permission(
    email: str = Path(...),
    current_user=Security(get_current_user, scopes=["base", "root"]),
):
    """Set permission for a user

    Set a permission for either a student or an admin
    Returns user details
    Args:
        user_id - id of user to be made an admin
        current_user - retrieved from login auth
    Returns:
        HTTP_200_OK if successful
    Raises:
        HTTP_404_NOT_FOUND if user not found
        HTTP_424_FAILED_DEPENDENCY if DB service fails
    """

    if current_user.is_admin is False:
        raise HTTPException(
            detail="Only admins can set permission",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user = await User.get_or_none(email=email)
    if not user:
        raise HTTPException(
            detail="User not found", status_code=status.HTTP_404_NOT_FOUND
        )
    if user.is_admin:
        user_set = await User.get(id=user.id).update(is_admin=False)
    else:
        user_set = await User.get(id=user.id).update(is_admin=True)
    if not user_set:
        raise HTTPException(
            detail="Permission not set",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return await User.get_or_none(email=email)


@router.put(
    "/verify-email/{otp}",
    response_model=EmailVerify,
    status_code=status.HTTP_200_OK,
)
async def email_verification(otp: str = Path(...)):
    """Verifies email of a new user

    Uses generated otp to match an existing user in the database
    Updates the email verified field to true and returns field
    Args:
        otp - a random str retrieved from the path
    Returns:
        HTTP_200_OK (with user details as defined in the response model)
    Raises:
        HTTP_401_UNAUTHORIZED if otp is invalid, expired or verification fails
    """
    user_id = otp_manager.get_otp_user(otp)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP is invalid or expired",
        )
        # Convert User-ID to a UUID after being stringified
    update_user = await User.get(id=UUID(user_id)).update(email_verified=True)
    if not update_user:
        raise HTTPException(
            "Email verification failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return "Email verification successful"


@router.post(
    "/login/",
    response_model=AuthResponse,
    name="auth:login",
    status_code=status.HTTP_200_OK,
)
async def login(data: LoginSchema):
    """Handles user login.

    Args:
        data - a pydantic schema that defines the user login details
    Return:
        HTTP_200_OK (with user details as defined in the response model)
        a jwt encoded token to be attached to request headers
    Raises:
        HTTP_401_UNAUTHORIZED if login credentials are incorrect
    """
    user = await User.get_or_none(email=data.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not verified",
        )
    # Check password.
    hashed_password = user.hashed_password
    is_valid_password: bool = pwd_context.verify(
        data.password, hashed_password
    )
    if not is_valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your email or password is incorrect.",
        )

    # Generate an auth token.
    jwt_data = JWTSchema(user_id=str(user.id))
    to_encode = jwt_data.dict()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"expire": str(expire)})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return AuthResponse(user=user, token=encoded_jwt)


@router.post(
    "/forgot-password/",
    name="auth:forgot-password",
    status_code=status.HTTP_200_OK,
)
async def forgot_password(data: ForgotPasswordSchema):
    """Handles forgot password request

    Args:
        data - a pydantic schema that defines forgot password detail
    Return:
        HTTP_200_OK response with password reset link sent in a mail service
    Raises:
        HTTP_401_UNAUTHORIZED if data doesn't match any entry in the DB
    """
    user = await User.get_or_none(email=data.email)
    if not user:
        raise HTTPException(
            detail="User does not exist",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    expire = datetime.now(timezone.utc) + timedelta(seconds=600)
    to_encode = {"user_id": str(user.id), "expire": str(expire)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # pending - send jwt token to user email as a background task
    return {"message": f"Password reset link sent to {data.email}"}


@router.put(
    "/reset-password/{token}",
    status_code=status.HTTP_200_OK,
)
async def password_reset(data: PasswordResetSchema, token: str = Path(...)):
    """Handles password reset request

    Args:
        data - a pydantic schema that defines the required reset details
        token - jwt encoded token sent a s path param
    Return:
        HTTP_200_OK response with a success message
    Raises:
        HTTP_401_UNAUTHORIZED if decoded token doesn't match any User entry
        HTTP_401_UNAUTHORIZED if decoded token is expired
        HTTP_424_FAILED_DEPENDENCY if password reset was unsuccessful
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodes token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        expire = payload.get("expire")
        if user_id is None or expire is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    # Check token expiration
    if str(datetime.now(timezone.utc)) > expire:
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid!",
        )

    # Fetches associated user from db
    user = await User.get_or_none(id=user_id)

    if not user:
        raise HTTPException(
            detail="User not found or does not exist",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    new_hashed_password = pwd_context.hash(data.password)
    pwd_reset = await User.get(id=user.id).update(
        hashed_password=new_hashed_password
    )

    if not pwd_reset:
        raise HTTPException(
            detail="Password reset unsuccessful",
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
        )
    return {"message": "Password reset successful"}


# @router.get(
#     "/logout/",
#     status_code=status.HTTP_200_OK,
# )
# async def logout(current_user=Security(get_current_user, scopes=["base"])):

#     jwt_data = JWTSchema(user_id=str(current_user.id))
#     to_encode = jwt_data.dict()
#     expire = datetime.now()
#     # expire = datetime.now(timezone.utc) - timedelta(days=1)
#     to_encode.update({"expire": str(expire)})

#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return AuthResponse(user=current_user, token=encoded_jwt)
