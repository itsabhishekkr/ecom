from fastapi import APIRouter, Depends
from app.core.getRole import require_provider
from app.models.dataConfig import get_db
from app.models.tables import Product
from app.schemas.provider_schemas import ProductAdd
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pro",tags=["Provider"])

@router.post("/products")
async def create_product(product: ProductAdd, db: Session = Depends(get_db), current_user=Depends(require_provider)):
    return await create_product(product, db)


