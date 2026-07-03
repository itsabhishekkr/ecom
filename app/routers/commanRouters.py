from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.dataConfig import get_db
from app.services.adminServices import get_categories

router = APIRouter(
    prefix="/com",
    tags=["Authentication"]
)

# Common endpoint for all users, including guests

@router.get("/categories")
async def all_categories(db: Session = Depends(get_db)):
    return await get_categories(db=db)

