
# fastapi ->ORM(Object relational mapping) Sqlachemy->  database(store) 

# fastapi -> create engine -> ORM(translate python code to sql) -> psycopg2 Driver
# (send SQL to MySQL) 

# update in the database -> session.commit() -> commit the changes to the database
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String,Boolean
from sqlalchemy.orm import relationship
from app.models.dataConfig import Base, get_db
from sqlalchemy.sql import func
# role base access control -> user role -> admin,student,teacher 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    # toway of connection
    todos = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"
    tid=Column(Integer,primary_key=True,index=True,autoincrement=True)
    title=Column(String,nullable=False)
    description=Column(String,nullable=False)
    completed=Column(Boolean,default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    user_id=Column(Integer,ForeignKey("users.id"))
    owner=relationship("User",back_populates="todos")