from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.getRole import get_current_user
from app.models.dataConfig import get_db
from app.models.tables import Category
from app.services.adminServices import get_categories
router = APIRouter(
    prefix="/com",
    tags=["Authentication"]
)

# comman for all the registered user only

@router.get("/categories")
async def all_categories(current_user=Depends(get_current_user),db: Session = Depends(get_db)):

    return await get_categories(db=db)

