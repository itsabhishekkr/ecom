from pydantic import BaseModel,EmailStr

class RegisterUser(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    role: str

class UserLogin(BaseModel):
    email:EmailStr
    password:str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str