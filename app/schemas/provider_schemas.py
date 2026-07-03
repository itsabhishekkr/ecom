from pydantic import BaseModel
from fastapi import Form


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int
    category_id: int

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        stock_quantity: int = Form(...),
        category_id: int = Form(...)
    ):
        return cls(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id
        )

class ProviderOrderStatusUpdate(BaseModel):
    status: str