from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.dataConfig import get_db
from app.core.getRole import get_current_user
from app.schemas.cart_schemas import CartAdd, CartItemUpdate, CartResponse
from app.services.cartServices import get_cart, add_to_cart, update_cart_item, delete_cart_item

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

@router.get("", response_model=CartResponse)
async def get_user_cart(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await get_cart(db, current_user)

@router.post("")
async def add_item_to_cart(
    item: CartAdd,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await add_to_cart(db, current_user, item.product_id, item.quantity)

@router.put("/{id}")
async def update_item_quantity(
    id: int,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await update_cart_item(db, current_user, id, item.quantity)

@router.delete("/{id}")
async def remove_item_from_cart(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await delete_cart_item(db, current_user, id)
