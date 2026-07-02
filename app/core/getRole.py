from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.models.dataConfig import get_db
from app.database.connection import SessionLocal
from app.models.tables import User, UserRole
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        id = payload.get("id")

        if not id:
            raise HTTPException(status_code=401,detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")
    
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=404,detail="User not found")

    if user.is_active == False:
        raise HTTPException(status_code=403,detail="Account blocked by admin")
    return user

def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403,detail="Access denied")
    return current_user

def require_provider(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.PROVIDER:
        raise HTTPException(status_code=403,detail="Access denied")
    return current_user

def require_customer(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403,detail="Access denied")
    return current_user
