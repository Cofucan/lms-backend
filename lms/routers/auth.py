## Libraries
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, status, Path, HTTPException

## Files, Models, Schemas, Dependencies
from models.user import User
from library.security.otp import otp_manager
from library.dependencies.utils import to_lower_case
from library.schemas.register import UserCreate, UserPublic, EmailVerify
from library.schemas.auth import (
    LoginSchema, AuthResponse, JWTSchema,
    PasswordResetSchema, ForgotPasswordSchema
    )
from config import SECRET_KEY, ALGORITHM


router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post(
    "/register/",
    response_model=AuthResponse,
    name="auth:register",
    status_code=status.HTTP_201_CREATED
)
async def register(data: UserCreate):
    """Creates a new user

    Registers a user in the database
    Returns user details when successfully registered
    Args:
        data - a pydantic schema that defines the user registration params
    Returns:
        HTTP_201_CREATED (with user details as defined in the response model)
        Sends otp via STMP as a background task
    Raises:
        HTTP_400_BAD_REQUEST if user exists or weak password
    """

    # Converting new user email to all lower-case before checking and storing in database
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
        hashed_password=hashed_password
    )

    # Printing the otp on the terminal.
    otp = otp_manager.create_otp(user_id=str(created_user.id))
    print(otp)
    return AuthResponse(user=created_user, token=otp)


@router.put(
    "/verify-email/{otp}",
    response_model=EmailVerify,
    status_code=status.HTTP_200_OK,
    # name="auth:verify-email"
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
        HTTP_401_UNAUTHORIZED if otp is invalid, expired or if verification failed
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
    # fetch  and return user after update the User.email_verified
    user = await User.get(id=UUID(user_id))
    return user


@router.post(
    "/login/",
    response_model=AuthResponse,
    name="auth:login",
    status_code=status.HTTP_200_OK
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your email or password is incorrect.",
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
    status_code=status.HTTP_200_OK
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
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    expire = datetime.now(timezone.utc) + timedelta(seconds=600)
    to_encode = {"user_id": str(user.id), "expire": str(expire)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(encoded_jwt)
    return {"message": f"Password reset link sent to {data.email}"}


@router.put(
    "/reset-password/{token}",
    name="auth:reset-password",
    status_code=status.HTTP_200_OK
)
async def password_reset(data: PasswordResetSchema, token: str = Path(...)):
    """Handles password reset request
    
    Args:
        data - a pydantic schema that defines the required details tp reset password
        token - jwt encoded token sent a s path param
    Return:
        HTTP_200_OK response with a success message
    Raises:
        HTTP_401_UNAUTHORIZED if decoded token doesn't match any User entry in the DB
        HTTP_401_UNAUTHORIZED if decoded token is expired
        HTTP_424_FAILED_DEPENDENCY if password reset was unsuccessful
    """
    credentials_exception = HTTPException(
        status_code=401,
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
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    new_hashed_password = pwd_context.hash(data.password)
    pwd_reset = await User.get(id=user.id).update(
        hashed_password=new_hashed_password
        )

    if not pwd_reset:
        raise HTTPException(
            detail="Password reset unsuccessful",
            status_code=status.HTTP_424_FAILED_DEPENDENCY
        )
    return {"message": "Password reset successful"}
      