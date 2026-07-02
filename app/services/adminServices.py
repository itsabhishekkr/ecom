from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.getRole import get_current_user, require_admin
from app.core.security import hash_password
from app.models.dataConfig import get_db
from app.models.tables import Category
from app.schemas.auth_schemas import CategoryCreate,CategoryUpdate


async def get_categories(db: Session):
    return db.query(Category).all()


async def create_category(category: CategoryCreate,db: Session):
    new_category = Category(name=category.name)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"message":"Category created successfully","category_id": new_category.id}


# PUT /categories/{id}
# Admin only
async def update_category(id: int,category: CategoryUpdate,db: Session):
    existing = (db.query(Category).filter(Category.id == id).first())
    existing.name = category.name

    db.commit()

    return {
        "message":"Updated successfully"
    }


# DELETE /categories/{id}
# Admin only
async def delete_category(
    id: int,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):

    category = (
        db.query(Category)
        .filter(Category.id == id)
        .first()
    )

    db.delete(category)
    db.commit()

    return {
        "message":"Deleted successfully"
    }