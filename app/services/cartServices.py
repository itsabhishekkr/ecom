from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tables import Cart, CartItem, Product

async def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

async def get_cart(db: Session, current_user):
    cart = await get_or_create_cart(db, current_user.id)
    items = []
    total = 0.0
    
    # Query CartItems joining with Product
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    for item in cart_items:
        product = item.product
        if product:
            price = float(product.price)
            item_total = price * item.quantity
            total += item_total
            items.append({
                "id": item.id,  # Include the cart item ID
                "product_id": product.id,
                "name": product.name,
                "quantity": item.quantity,
                "price": price
            })
            
    return {
        "items": items,
        "total": total
    }

async def add_to_cart(db: Session, current_user, product_id: int, quantity: int):
    cart = await get_or_create_cart(db, current_user.id)
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if product.stock_quantity < quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {product.stock_quantity}")
        
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()
    
    if cart_item:
        new_quantity = cart_item.quantity + quantity
        if product.stock_quantity < new_quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for requested total quantity: {new_quantity}")
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)
        
    try:
        db.commit()
        return {"message": "Added to cart"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def update_cart_item(db: Session, current_user, cart_item_id: int, quantity: int):
    cart = await get_or_create_cart(db, current_user.id)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
        
    product = cart_item.product
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if product.stock_quantity < quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {product.stock_quantity}")
        
    cart_item.quantity = quantity
    try:
        db.commit()
        return {"message": "Cart item updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def delete_cart_item(db: Session, current_user, cart_item_id: int):
    cart = await get_or_create_cart(db, current_user.id)
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
        
    try:
        db.delete(cart_item)
        db.commit()
        return {"message": "Cart item deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
