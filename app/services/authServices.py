from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import RegisterUser,UserLogin
from app.models.tables import User,UserRole
from app.models.dataConfig import declarative_base,get_db
from app.core.security import hash_password,verify_password
from app.core.tokenveryfy import create_access_token,decode_token

async def register(user: RegisterUser,db: Session):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return {"message": "Email already exists"}
     # Block public admin creation
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403,detail="Admin registration is not allowed")
    
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        password_hash=hash_password(
            user.password
        ),
        role=user.role,
        is_active=(False
            if user.role == UserRole.PROVIDER
            else True
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully","user_id": new_user.id}


async def userLogin(user: UserLogin,db: Session):
    existing_user = (db.query(User).filter(User.email == user.email).first())

    if not existing_user:
        raise HTTPException(status_code=404,detail="Wrong email")

    if not verify_password(user.password,existing_user.password_hash): 
        raise HTTPException(status_code=401,detail="Wrong password")
    
    token = create_access_token({"id": existing_user.id,"email": existing_user.email,"role":existing_user.role})

    return {"access_token": token,"token_type": "bearer"}

async def logOut(token: str,db: Session):
    decoded_token = decode_token(token)
    user_id = decoded_token.get("id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException