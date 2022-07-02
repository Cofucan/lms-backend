import email
from uuid import UUID
from fastapi import APIRouter, status,Path, HTTPException
from library.schemas.register import UserPublic, EmailVerify
from models.user import User
from library.schemas.register import UserCreate
from passlib.context import CryptContext
from library.security.otp import otp_manager
from library.schemas.auth import (
    AuthResponse,
    LoginSchema,
    JWTSchema,
)
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM
from jose import jwt


router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register/", response_model=UserPublic, name='auth:register', status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):

    email_exist = await User.get_or_none(email=data.email)
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )
    password = data.password
    # password strength check. Throws an error if password doesn't contain
    # uppercase, lowercase, digit and a special character
    if (
        len(password) < 8
        or password.lower() == password
        or password.upper() == password
        or password.isalnum()
        or not any(i.isdigit() for i in password)
    ):
        raise HTTPException(
            detail={
                "password": "Your Password Is Weak",
                "Hint": "Min. 8 characters, 1 Uppercase, 1 lowercase, 1 number, and 1 special character",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    hashed_password = pwd_context.hash(password)
    created_user = await User.create(
        **data.dict(exclude_unset=True, exclude={"password"}),
        hashed_password=hashed_password
    )
    otp = otp_manager.create_otp(user_id=str(created_user.id))
    # You will only get the OTP in your terminal for now.
    print(otp)
    return created_user


@router.put("/verify-email/{otp}", response_model=EmailVerify, name="auth:verify-email")
async def email_verification(otp: str = Path(...)):
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


"""Login to account"""


@router.post("/login/", response_model=AuthResponse, name="auth:login")
async def Login(data: LoginSchema):
    """handle user Login"""
    user = await User.get_or_none(email=data.username_or_email)

    # Extract User Details
    if user is None:
        user = await User.get_or_none(username=data.username_or_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or email",
        )

    """check if password is correct"""
    hashed_password = user.hashed_password
    is_password_valid: bool = pwd_context.verify(
        data.password, hashed_password
    )
    if is_password_valid is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password Incorrect",
        )

    """Generate the JWT token"""
    jwt_data = JWTSchema(user_id=str(user.id))

    to_encode = jwt_data.dict()

    """encode jwt token(call encode function from jose)"""

    expire = expire = str(
        datetime.now(timezone.utc) + timedelta(minutes=43200)
    )
    to_encode.update({"expire": str(expire)})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return AuthResponse(user=user, token=encoded_jwt)
