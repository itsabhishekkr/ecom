from pydantic import BaseModel
from typing import List, Optional

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category_id: Optional[int]
    image_url: Optional[str]

    class Config:
        from_attributes = True

class ProductListItem(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    total: int
    page: int
    data: List[ProductListItem]
