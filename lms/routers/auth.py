import email
from uuid import UUID
from fastapi import APIRouter, status,Path, HTTPException
from library.schemas.register import UserPublic, EmailVerify
from models.user import User
from library.schemas.register import UserCreate
from passlib.context import CryptContext

from models.user import User
from library.dependencies.utils import to_lower_case
from library.schemas.register import UserCreate
from library.schemas.register import UserPublic, EmailVerify
from library.security.otp import otp_manager
from library.schemas.auth import (
    AuthResponse,
    LoginSchema,
    JWTSchema,
    ForgotPassword,
    ResetPassword
)

from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM
from jose import jwt

router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register/", response_model=UserPublic, name='auth:register', status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):

    # Converting new user email to all lower-case before checking and storing in database
    converted_email = to_lower_case(data.email)

    email_exist = await User.exists(email=converted_email)
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist",
        )
        
    password = data.password
    # password strength check. Throws an error if password doesn't contain
    # uppercase, lowercase, digit and a special character
    if (password.lower() == password
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
        **data.dict(exclude_unset=True, exclude={"email", "password"}),
        email=converted_email,
        hashed_password=hashed_password
    )

    # Printing the otp on the terminal.
    otp = otp_manager.create_otp(user_id=str(created_user.id))
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

@router.post("/login/", response_model=AuthResponse)
async def login(data: LoginSchema):
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
    if not is_password_valid:
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
    to_encode.update({"expire": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return AuthResponse(user=user, token=encoded_jwt)


@router.post("/forgot-password/", response_model=AuthResponse)
async def forgot_password(data: ForgotPassword):
    """Verify email and retrieve user details"""
    user = await User.get_or_none(email=data.email)   
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )

    """Generate the JWT token for valid user"""    
    jwt_data = JWTSchema(user_id=str(user.id))    

    to_encode = jwt_data.dict()
    expire = datetime.now(timezone.utc) + timedelta(seconds=600)
    to_encode.update({"expire": str(expire)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return AuthResponse(user=user, token=encoded_jwt)



@router.put("/reset-password/{token}", response_model=UserPublic)
async def reset_password(data: ResetPassword, token: str = Path(...)):
    """Decode token to get user"""    
    try:        
        decoded_data = jwt.decode(
            token, str(SECRET_KEY), algorithms=[ALGORITHM]
        )
        user_id = decoded_data['user_id']
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User detail could not be processed."
        )    
     
    """Confirm and get user with decoded user_id"""
    user = await User.get_or_none(id=UUID(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    """Reset user password for valid user"""
    password = data.password
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
    await User.get(id=UUID(user_id)).update(
    hashed_password=hashed_password
    )
    updated_user =  await User.get(id=UUID(user_id))          
    return updated_user   
