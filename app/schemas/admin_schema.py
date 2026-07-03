from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    role: str
    is_active: bool

class UserStatusUpdate(BaseModel):
    is_active: bool