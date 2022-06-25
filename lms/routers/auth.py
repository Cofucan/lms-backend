from curses.ascii import CR
from http.client import HTTPException
from fastapi import APIRouter,HTTPException, status
from models.user import User
from passlib.context import CryptContext

from lms.library.schemas.auth import LoginSchema

router = APIRouter(prefix="/auth")
pwd_context = CryptContext(schemes=['bcrypt'])

"""Signin to account"""
@router.post("/Signin/", response_model=str)
async def Signin(data: LoginSchema):
    """handle user Signup"""
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
    if is_password_valid == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password Incorrect"
        )