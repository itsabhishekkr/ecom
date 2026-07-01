from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import RegisterUser,UserLogin,LoginResponse
from app.services.authServices import register,userLogin
from app.models.dataConfig import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
async def register_user(user: RegisterUser,db: Session = Depends(get_db)):
    return await register(user, db)

@router.post("/login")
async def login_user(user: UserLogin,db: Session = Depends(get_db))->LoginResponse:
    return await userLogin(user, db)

@router.post("/logout")
async def logout(response: Response):

    response.delete_cookie(
        key="access_token"
    )

    return {
        "message":"Logged out successfully"
    }