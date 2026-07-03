from pydantic import BaseModel

class PaymentCreate(BaseModel):
    order_id: int

class PaymentCreateResponse(BaseModel):
    payment_url: str

class PaymentVerify(BaseModel):
    payment_id: str

class PaymentVerifyResponse(BaseModel):
    status: str
