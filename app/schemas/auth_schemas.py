from pydantic import BaseModel,EmailStr

class UserRegistration(BaseModel):
    name:str
    email:EmailStr
    password:str


class UserLogin(BaseModel):
    email:EmailStr
    password:str
