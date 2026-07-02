from pydantic import BaseModel, Field

class ProductAdd(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int = Field(default=0, ge=0)
    category_id: int
    provider_id: int
    image_url: str = Field(default=None, description="URL of the product image")


