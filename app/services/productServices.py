from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.tables import Product, Category, UserRole
from app.schemas.product_schemas import ProductUpdate
from app.utils.upload import save_product_image
from typing import Optional

async def get_products(
    db: Session,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    page: int = 1,
    limit: int = 10
):
    query = db.query(Product)
    
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
        
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    total = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()
    
    data = [{"id": p.id, "name": p.name, "price": float(p.price)} for p in products]
    
    return {
        "total": total,
        "page": page,
        "data": data
    }

async def get_product_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "stock_quantity": product.stock_quantity,
        "category_id": product.category_id,
        "image_url": product.image_url
    }

async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    image,
    db: Session,
    current_user
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Check permissions: only admin or the provider who owns the product can modify it
    if current_user.role != UserRole.ADMIN and product.provider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    if product_data.category_id is not None:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
            
    # Update fields
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.stock_quantity is not None:
        product.stock_quantity = product_data.stock_quantity
    if product_data.category_id is not None:
        product.category_id = product_data.category_id
        
    # If image is uploaded
    if image:
        image_url = save_product_image(image)
        product.image_url = image_url
        
    try:
        db.commit()
        db.refresh(product)
        return {
            "message": "Product updated successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "image_url": product.image_url
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def delete_product(product_id: int, db: Session, current_user):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Check permissions: only admin or the provider who owns the product can delete it
    if current_user.role != UserRole.ADMIN and product.provider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    try:
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
