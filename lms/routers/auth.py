from http.client import HTTPException
from fastapi import APIRouter,HTTPException, status, Response
from models.user import User
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM
from jose import jwt


from lms.library.schemas.auth import LoginSchema,JWTSchema, AuthResponse

router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=['bcrypt'])

"""Login to account"""
@router.post("/Login/", response_model=str)
async def Login(data: LoginSchema):
    """handle user Login"""
    user = await User.get_or_none(email=data.username_or_email)

    # Extract User Details 
    if user is None:
        user = await User.get_or_none(username=data.username_or_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Incorrect username or email"
         )

    """check if password is correct"""
    hashed_password = user.hashed_password
    is_password_valid: bool = pwd_context.verify(data.password, hashed_password)
    if is_password_valid is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password Incorrect"
        )
    return Response(
        status_code=status.HTTP_200_OK, 
        detail="Login Successful"
        )
    