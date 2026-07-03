import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tables import Order, Payment

async def create_payment(db: Session, current_user, order_id: int):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.status != "pending":
        raise HTTPException(status_code=400, detail=f"Order cannot be paid because status is '{order.status}'")
        
    payment_id = f"payment_{uuid.uuid4().hex[:12]}"
    
    new_payment = Payment(
        order_id=order.id,
        payment_id=payment_id,
        amount=order.total_amount,
        status="pending"
    )
    
    try:
        db.add(new_payment)
        db.commit()
        
        # Return mock gateway URL
        mock_url = f"http://localhost:8000/payments/mock-gateway?payment_id={payment_id}&amount={float(order.total_amount)}"
        return {
            "payment_url": mock_url
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def verify_payment(db: Session, payment_id: str):
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment transaction not found")
        
    if payment.status == "success":
        return {"status": "success"}
        
    try:
        payment.status = "success"
        order = payment.order
        if order:
            order.status = "processing"  # mark as paid / processing
            
        db.commit()
        return {
            "status": "success"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
