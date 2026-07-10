from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tables import Cart, CartItem, Product, Order, OrderItem, Address, UserRole, OrderStatus

async def create_order(db: Session, current_user, address_id: int, payment_method: str):
    # Get Cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    # Verify address
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found or doesn't belong to you")
        
    # Validate stock
    for item in cart_items:
        product = item.product
        if not product:
            raise HTTPException(status_code=404, detail=f"Product ID {item.product_id} no longer exists")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock_quantity}")
            
    # Calculate total
    total_amount = sum(float(item.product.price) * item.quantity for item in cart_items)
    
    try:
        # Create Order
        order = Order(
            user_id=current_user.id,
            address_id=address_id,
            payment_method=payment_method,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        db.add(order)
        db.flush()  # populate order.id
        
        # Create Order Items and deduct stock
        for item in cart_items:
            product = item.product
            # Deduct stock
            product.stock_quantity -= item.quantity
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )
            db.add(order_item)
            
        # Empty cart items
        for item in cart_items:
            db.delete(item)
            
        db.commit()
        db.refresh(order)
        return {
            "order_id": order.id,
            "status": order.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def get_orders(db: Session, current_user):
    # Retrieve customer orders
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return [
        {
            "order_id": o.id,
            "status": o.status,
            "total": float(o.total_amount)
        } for o in orders
    ]

async def get_order_by_id(db: Session, current_user, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check permissions
    if current_user.role != UserRole.ADMIN and order.user_id != current_user.id:
        # Wait, if current_user is a provider, can they view this order?
        # Provider dashboard has /provider/orders which is handled separately.
        # Customer GET /orders/{id} only allows the customer or admin.
        raise HTTPException(status_code=403, detail="Access denied")
        
    products = []
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    for item in order_items:
        products.append({
            "product_id": item.product_id,
            "name": item.product.name if item.product else "Unknown Product",
            "quantity": item.quantity,
            "price": float(item.price)
        })
        
    return {
        "order_id": order.id,
        "status": order.status,
        "products": products,
        "total": float(order.total_amount),
        "address_id": order.address_id,
        "payment_method": order.payment_method
    }
