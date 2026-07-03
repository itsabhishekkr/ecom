from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.dataConfig import get_db
from app.core.getRole import get_current_user
from app.schemas.order_schemas import OrderCreate, OrderResponse, OrderListResponse, OrderDetailResponse
from app.services.orderServices import create_order, get_orders, get_order_by_id
from typing import List

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

@router.post("", response_model=OrderResponse)
async def checkout(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await create_order(db, current_user, order_data.address_id, order_data.payment_method)

@router.get("", response_model=List[OrderListResponse])
async def list_user_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await get_orders(db, current_user)

@router.get("/{id}", response_model=OrderDetailResponse)
async def get_user_order(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await get_order_by_id(db, current_user, id)
