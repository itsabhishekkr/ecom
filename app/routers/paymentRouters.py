from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.dataConfig import get_db
from app.core.getRole import get_current_user
from app.schemas.payment_schemas import PaymentCreate, PaymentCreateResponse, PaymentVerify, PaymentVerifyResponse
from app.services.paymentServices import create_payment, verify_payment

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.post("/create", response_model=PaymentCreateResponse)
async def initiate_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await create_payment(db, current_user, payment_data.order_id)

@router.post("/verify", response_model=PaymentVerifyResponse)
async def check_payment(
    verification_data: PaymentVerify,
    db: Session = Depends(get_db)
):
    return await verify_payment(
        db,
        verification_data.payment_id,
        verification_data.razorpay_order_id,
        verification_data.razorpay_payment_id,
        verification_data.razorpay_signature,
    )
