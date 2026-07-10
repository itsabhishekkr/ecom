from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.core.getRole import require_provider
from app.models.dataConfig import get_db
from app.schemas.provider_schemas import ProductCreate, ProviderOrderStatusUpdate
from sqlalchemy.orm import Session
from app.services.providerServices import (
    create_product,
    get_provider_dashboard,
    get_provider_orders,
    update_provider_order_status
)

router = APIRouter(prefix="/provider", tags=["Provider Dashboard"])
legacy_pro_router = APIRouter(prefix="/pro", tags=["Provider Legacy"])

# Legacy endpoint /pro/products
@legacy_pro_router.post("/products")
async def create_product_legacy(
    product: ProductCreate = Depends(ProductCreate.as_form),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    return await create_product(product, image, db, current_user)

@router.get("/dashboard")
async def provider_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    return await get_provider_dashboard(db, current_user)

@router.get("/orders")
async def provider_orders(
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    return await get_provider_orders(db, current_user)


@router.get("/products")
async def provider_products(
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    from app.services.productServices import get_products_for_provider
    return await get_products_for_provider(db, current_user.id)

@router.put("/orders/{id}")
async def update_order_status(
    id: int,
    order_status: ProviderOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    return await update_provider_order_status(db, current_user, id, order_status.status)