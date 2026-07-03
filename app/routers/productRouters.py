from fastapi import APIRouter, Depends, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.models.dataConfig import get_db
from app.core.getRole import get_current_user, require_provider, require_admin
from app.models.tables import Product
from app.schemas.product_schemas import ProductUpdate, ProductResponse, ProductListResponse
from app.schemas.provider_schemas import ProductCreate
from app.services.productServices import get_products, get_product_by_id, update_product, delete_product
from app.services.providerServices import create_product as service_create_product
from typing import Optional

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("")
async def list_products(
    search: Optional[str] = Query(None),
    category: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return await get_products(db, search=search, category_id=category, page=page, limit=limit)

@router.get("/{id}", response_model=ProductResponse)
async def get_product(id: int, db: Session = Depends(get_db)):
    return await get_product_by_id(db, id)

@router.post("")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    # Map form fields to ProductCreate
    product_data = ProductCreate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id
    )
    return await service_create_product(product_data, image, db, current_user)

@router.put("/{id}")
async def update_product_endpoint(
    id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    product_data = ProductUpdate(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id
    )
    return await update_product(id, product_data, image, db, current_user)

@router.delete("/{id}")
async def delete_product_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_provider)
):
    return await delete_product(id, db, current_user)
