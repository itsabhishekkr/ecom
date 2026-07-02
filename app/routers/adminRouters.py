from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.getRole import get_current_user,require_admin
from app.models.dataConfig import get_db
from app.models.tables import Category
from app.schemas.auth_schemas import CategoryCreate,CategoryUpdate
from app.services.adminServices import create_category,update_category,delete_category
router = APIRouter(
    prefix="/admin",
    tags=["Authentication"]
)

@router.post("/categories")
async def create_new_category(category: CategoryCreate,current_user=Depends(require_admin),db: Session = Depends(get_db)):
    return await create_category(category, db=db)

@router.put("/categories/{id}")
async def update_existing_category(id: int,category: CategoryUpdate,current_user=Depends(require_admin),db: Session = Depends(get_db)):
    return await update_category(id, category,db)