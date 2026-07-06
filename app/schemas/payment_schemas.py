from typing import Optional
from pydantic import BaseModel


class PaymentCreate(BaseModel):
    order_id: int


class PaymentCreateResponse(BaseModel):
    payment_id: str
    razorpay_order_id: str
    amount: float
    currency: str
    key_id: str
    order_id: int
    payment_url: Optional[str] = None


class PaymentVerify(BaseModel):
    payment_id: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None


class PaymentVerifyResponse(BaseModel):
    status: str
