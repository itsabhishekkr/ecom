from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.tables import Category, User, Product, Order, UserRole
from app.schemas.auth_schemas import CategoryCreate, CategoryUpdate

async def get_categories(db: Session):
    return db.query(Category).all()

async def create_category(category: CategoryCreate, db: Session):
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"message": "Category created successfully", "category_id": new_category.id}

async def update_category(id: int, category: CategoryUpdate, db: Session):
    existing = db.query(Category).filter(Category.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Category not found")
    
    existing.name = category.name
    db.commit()
    return {"message": "Updated successfully"}

async def delete_category(id: int, db: Session):
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Deleted successfully"}

async def get_all_users(db: Session):
    return db.query(User).all()

async def get_admin_dashboard(db: Session):
    total_users = db.query(User).filter(User.role != UserRole.ADMIN).count()
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(func.sum(Order.total_amount)).scalar()
    
    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue) if total_revenue is not None else 0.0
    }

async def get_admin_users(db: Session):
    users = db.query(User).filter(User.role == UserRole.CUSTOMER).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "phone": u.phone,
            "is_active": u.is_active
        } for u in users
    ]

async def get_admin_providers(db: Session):
    providers = db.query(User).filter(User.role == UserRole.PROVIDER).all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "phone": u.phone,
            "is_active": u.is_active
        } for u in providers
    ]

async def toggle_user_active(db: Session, user_id: int, is_active: bool):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot change Admin status")
        
    user.is_active = is_active
    db.commit()
    return {"message": f"User active status set to {is_active}"}