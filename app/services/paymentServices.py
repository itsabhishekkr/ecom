import hashlib
import hmac
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_razorpay_key_id, get_razorpay_secret
from app.models.tables import Order, Payment, PaymentStatus, OrderStatus
from dotenv import load_dotenv
load_dotenv()

RAZORPAY_KEY_ID=os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET=os.getenv("RAZORPAY_SECRET")


async def create_razorpay_order(order: Order):
    try:
        import razorpay
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Razorpay SDK is not available: {exc}") from exc

    if not RAZORPAY_KEY_ID or not RAZORPAY_SECRET:
        raise HTTPException(status_code=500, detail="Razorpay API credentials are missing")

    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))
        amount_in_paise = int(float(order.total_amount) * 100)
        return client.order.create(
            {
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": f"order_{order.id}",
                "notes": {"order_id": str(order.id)},
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Razorpay order creation failed: {exc}") from exc


async def create_payment(db: Session, current_user, order_id: int):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    current_status = getattr(order.status, "value", order.status)
    if str(current_status).lower() != OrderStatus.PENDING.value:
        raise HTTPException(status_code=400, detail=f"Order cannot be paid because status is '{order.status}'")

    try:
        razorpay_order = await create_razorpay_order(order)
        new_payment = Payment(
            order_id=order.id,
            amount=order.total_amount,
            status=PaymentStatus.PENDING,
            payment_method="online",
            razorpay_order_id=razorpay_order.get("id"),
        )

        db.add(new_payment)
        db.commit()

        return {
            "payment_id": str(new_payment.id),
            "razorpay_order_id": razorpay_order.get("id"),
            "amount": float(order.total_amount),
            "currency": razorpay_order.get("currency", "INR"),
            "key_id": get_razorpay_key_id(),
            "order_id": order.id,
            "payment_url": f"/payments/verify?payment_id={new_payment.id}",
        }
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(exc)}") from exc


async def verify_payment(
    db: Session,
    payment_id: str,
    razorpay_order_id: str | None = None,
    razorpay_payment_id: str | None = None,
    razorpay_signature: str | None = None,
):
    payment = db.query(Payment).filter(Payment.id == int(payment_id)).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment transaction not found")

    if payment.status == PaymentStatus.SUCCESS:
        return {"status": "success"}

    if razorpay_order_id and razorpay_payment_id and razorpay_signature:
        secret = get_razorpay_secret().encode()
        payload = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
        expected_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_signature, razorpay_signature):
            raise HTTPException(status_code=400, detail="Razorpay signature verification failed")

    try:
        payment.status = PaymentStatus.SUCCESS
        payment.razorpay_payment_id = razorpay_payment_id
        order = payment.order
        if order:
            order.status = "processing"

        db.commit()
        return {"status": "success"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}") from exc
