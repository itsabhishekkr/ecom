from pydantic import BaseModel
from typing import List, Optional

class OrderCreate(BaseModel):
    address_id: int
    payment_method: Optional[str] = "online"

class OrderResponse(BaseModel):
    order_id: int
    status: str

class OrderListResponse(BaseModel):
    order_id: int
    status: str
    total: float

class OrderProductItem(BaseModel):
    product_id: int
    name: str
    quantity: int
    price: float

class OrderDetailResponse(BaseModel):
    order_id: int
    status: str
    products: List[OrderProductItem]
    total: float
    address_id: Optional[int]
    payment_method: str
