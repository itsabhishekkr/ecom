from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.tables import Product, Category, Order, OrderItem, User, OrderStatus
from app.utils.upload import save_product_image

async def create_product(product, image, db: Session, current_user):
    # Check category exists
    category = (
        db.query(Category)
        .filter(Category.id == product.category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Save image and get URL
    image_url = save_product_image(image)

    # Create product object
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        image_url=image_url,
        provider_id=current_user.id
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {
            "message": "Product created successfully",
            "product": {
                "id": new_product.id,
                "name": new_product.name,
                "price": float(new_product.price),
                "stock_quantity": new_product.stock_quantity,
                "image_url": new_product.image_url
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

async def get_provider_dashboard(db: Session, current_user):
    total_products = db.query(Product).filter(Product.provider_id == current_user.id).count()
    
    total_orders = db.query(OrderItem.order_id).join(Product).filter(
        Product.provider_id == current_user.id
    ).distinct().count()
    
    total_sales = db.query(func.sum(OrderItem.price * OrderItem.quantity)).join(Product).filter(
        Product.provider_id == current_user.id
    ).scalar()
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_sales": float(total_sales) if total_sales is not None else 0.0
    }

async def get_provider_orders(db: Session, current_user):
    orders = (
        db.query(Order)
        .join(OrderItem)
        .join(Product)
        .filter(Product.provider_id == current_user.id)
        .distinct()
        .all()
    )

    results = []
    for o in orders:
        # Only include order items that belong to this provider
        items = (
            db.query(OrderItem)
            .join(Product)
            .filter(OrderItem.order_id == o.id, Product.provider_id == current_user.id)
            .all()
        )

        products = []
        for item in items:
            prod = item.product
            products.append({
                "product_id": prod.id if prod else item.product_id,
                "name": prod.name if prod else "Unknown",
                "quantity": item.quantity,
                "price": float(item.price)
            })

        total_for_provider = sum(p["price"] * p["quantity"] for p in products)

        results.append({
            "order_id": o.id,
            "customer": o.user.full_name if o.user else "Unknown",
            "status": o.status.value if hasattr(o.status, "value") else o.status,
            "items": products,
            "total_for_provider": float(total_for_provider),
        })

    return results

async def update_provider_order_status(db: Session, current_user, order_id: int, status: str):
    # Verify the order exists and contains at least one product from this provider
    order_has_provider_product = db.query(OrderItem).join(Product).filter(
        OrderItem.order_id == order_id,
        Product.provider_id == current_user.id
    ).first()
    
    if not order_has_provider_product:
        raise HTTPException(status_code=404, detail="Order not found or does not contain your products")
        
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if status not in {s.value for s in OrderStatus}:
        raise HTTPException(status_code=400, detail="Invalid order status")

    try:
        order.status = OrderStatus(status)
        db.commit()
        return {"message": f"Order status updated to {status}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")