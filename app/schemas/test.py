from pydantic import BaseModel, Field

class Student(BaseModel):
    name : str
    age : int
    email : str
    phone : str
    batch : str
