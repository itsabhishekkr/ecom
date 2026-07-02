from fastapi import FastAPI
from app.schemas.test import Student
from app.models.dataConfig import Base
from app.database.connection import engine, SessionLocal
from app.models import tables  # noqa: F401
from app.routers.auth import router as auth_routers
from app.routers.adminRouters import router as admin_routers
from app.routers.commanRouters import router as comman_routers
from app.routers.seed_admin import seed_admin
app = FastAPI()
Base.metadata.create_all(bind=engine)
## first call the seed admin function here to create the admin user in the database
# create a session and pass it to the seeder, then close the session
db = SessionLocal()
try:
	seed_admin(db)
finally:
	db.close()
# # include routers
app.include_router(auth_routers)
app.include_router(admin_routers)
app.include_router(comman_routers)


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.post("/items/path/{user_id}")
# def update_item(user_id: int):

#     return {"user_id": user_id, "item": "This is path parameter"}

# @app.post("/items/query")
# def update_item(user_id: int):

#     return {"user_id": user_id, "item": "This is a query parameter"}


# # path and query parameter
# @app.post("/items/path_query/{user_id}")
# def update_item(user_id: int, item: Student):

#     return {"user_id": user_id, "item_id": "this is item id", "item": "This is a path and query parameter"}

# @app.post("/items/path_query/{user_id}")
# def update_item(user_id: int, roll: int , name: str):

#     return {"user_id": user_id, "roll": roll, "name": name}

# @app.get("/items/is/{item_id}")
# async def read_item(item_id: str, q: str | None = None):
#     if q:
#         return {"item_id": item_id, "q": q}
#     return {"item_id": item_id}

# @app.post("/items/pathquery/{user_id}")
# def update_item(user_id: int,  name: str,roll: int | None = None):
#     if roll:
#         return {"user_id": user_id, "roll": roll, "name": name}
#     return {"user_id": user_id, "roll": roll}