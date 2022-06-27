from datetime import datetime, timedelta, timezone
import email
from this import s
from uuid import UUID
from fastapi import APIRouter, status, Response, Path, HTTPException
from library.schemas.register import UserPublic, EmailVerify
from config import ALGORITHM, SECRET_KEY
from library.schemas.auth import JWTSchema, LoginSchema
from models.user import User
from library.schemas.register import UserCreate
from passlib.context import CryptContext
from library.security.otp import otp_manager
from library.schemas.auth import AuthResponse
from jose import jwt


router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=['bcrypt'],deprecated="auto")



@router.post("/register/", response_model=UserPublic)
async def register(data: UserCreate):

    email_exist = await User.get_or_none(email=data.email)
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User with this email already exist"
        )
    password = data.password
    # password strength check. Throws an error if password doesn't contain
    # uppercase, lowercase, digit and a special character
    if len(password) < 8 or password.lower() == password\
            or password.upper() == password or password.isalnum()\
            or not any(i.isdigit() for i in password): 
            raise HTTPException(detail={
                'password':'Your Password Is Weak',
                'Hint': 'Min. 8 characters, 1 Uppercase, 1 lowercase, 1 number, and 1 special character'
            }, status_code= status.HTTP_400_BAD_REQUEST)
    hashed_password = pwd_context.hash(password)
    created_user = await User.create(**data.dict(exclude_unset=True, exclude={"password"}), hashed_password=hashed_password)
    otp = otp_manager.create_otp(user_id=str(created_user.id))
    # You will only get the OTP in your terminal for now. 
    print(otp)
    return created_user



@router.put("/verify-email/{otp}", response_model=EmailVerify)
async def email_verification(otp: str = Path(...)):
    user_id = otp_manager.get_otp_user(otp)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="OTP is invalid or expired"
        )
        # Convert User-ID to a UUID after being stringified
    update_user = await User.get(id=UUID(user_id)).update(
        email_verified = True
    )
    if not update_user:
        raise HTTPException("Email verification failed", status_code=status.HTTP_401_UNAUTHORIZED)
    # fetch  and return user after update the User.email_verified
    user = await User.get(id=UUID(user_id))
    return user
    



@router.post("/login/", response_model=AuthResponse)
async def user_login(data: LoginSchema):
    get_user_by_email = await User.get_or_none(email=data.username_or_email)
    if get_user_by_email is None:
        get_user_by_username = await User.get_or_none(username=data.username_or_email)
        if get_user_by_username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid login credentials"
            )
    password = data.password
    hashed_passsword = get_user_by_email.hashed_password
    verify_password: bool = pwd_context.verify(password, hashed_passsword)
    if verify_password is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= "Incorrect password"
        )
    

    jwt_data = JWTSchema(user_id=str(get_user_by_email.id))
    expire= (datetime.now(timezone.utc) + timedelta(days=0, minutes=15))
    jwt_data_encoded = jwt_data.dict()
    jwt_data_encoded.update({"expire": str(expire)})



    jwt_encode = jwt.encode(jwt_data_encoded, SECRET_KEY, algorithm=ALGORITHM)
    return AuthResponse(
        user = get_user_by_email,
        token=jwt_encode
    )