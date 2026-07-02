from app.core.getRole import get_current_user, require_admin,require_provider,require_customer
from fastapi import APIRouter, Depends
from app.schemas.provider_schemas import ProductAdd
from app.models.tables import Product
from sqlalchemy.orm import Session

async def create_product(product: ProductAdd, db: Session):
    
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        provider_id=product.provider_id,
        image_url=product.image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Product created successfully", "product_id": new_product.id}
