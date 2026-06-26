from fastapi import FastAPI
from app.schemas.test import Student
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/items/path/{user_id}")
def update_item(user_id: int):

    return {"user_id": user_id, "item": "This is path parameter"}

@app.post("/items/query")
def update_item(user_id: int):

    return {"user_id": user_id, "item": "This is a query parameter"}


# path and query parameter
@app.post("/items/path_query/{user_id}")
def update_item(user_id: int, item: Student):

    return {"user_id": user_id, "item_id": "this is item id", "item": "This is a path and query parameter"}

@app.post("/items/path_query/{user_id}")
def update_item(user_id: int, roll: int , name: str):

    return {"user_id": user_id, "roll": roll, "name": name}

@app.get("/items/is/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

@app.post("/items/pathquery/{user_id}")
def update_item(user_id: int,  name: str,roll: int | None = None):
    if roll:
        return {"user_id": user_id, "roll": roll, "name": name}
    return {"user_id": user_id, "roll": roll}