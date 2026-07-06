
# fastapi ->ORM(Object relational mapping) Sqlachemy->  database(store) 

# fastapi -> create engine -> ORM(translate python code to sql) -> psycopg2 Driver
# (send SQL to MySQL) 

# update in the database -> session.commit() -> commit the changes to the database
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    Numeric,
    ForeignKey,
    DateTime,
    Enum
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.models.dataConfig import Base


# ====================================
# ENUMS
# ====================================

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


# ====================================
# USERS
# ====================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    phone = Column(
        String(20)
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        Enum(UserRole),
        default=UserRole.CUSTOMER
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        index=True
    )

    # Relationships

    addresses = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete"
    )

    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete"
    )

    products = relationship(
        "Product",
        back_populates="provider",
        cascade="all, delete"
    )


# ====================================
# ADDRESSES
# ====================================

class Address(Base):
    __tablename__ = "addresses"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    address_line1 = Column(
        Text,
        nullable=False
    )

    address_line2 = Column(Text)

    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))

    latitude = Column(Float)
    longitude = Column(Float)

    is_default = Column(
        Boolean,
        default=False
    )

    user = relationship(
        "User",
        back_populates="addresses"
    )


# ====================================
# CATEGORIES
# ====================================

class Category(Base):
    __tablename__ = "categories"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    products = relationship(
        "Product",
        back_populates="category"
    )


# ====================================
# PRODUCTS
# ====================================

class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(Text)

    price = Column(
        Numeric(10,2),
        nullable=False
    )

    stock_quantity = Column(
        Integer,
        default=0
    )

    image_url = Column(Text)

    is_active = Column(
        Boolean,
        default=True
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        index=True
    )

    provider_id = Column(
        Integer,
        ForeignKey("users.id"),
        index=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    category = relationship(
        "Category",
        back_populates="products"
    )

    provider = relationship(
        "User",
        back_populates="products"
    )


# ====================================
# CART
# ====================================

class Cart(Base):
    __tablename__ = "carts"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True
    )

    user = relationship(
        "User"
    )

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete"
    )


# ====================================
# CART ITEMS
# ====================================

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    cart_id = Column(
        Integer,
        ForeignKey(
            "carts.id",
            ondelete="CASCADE"
        )
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    quantity = Column(
        Integer,
        default=1
    )

    cart = relationship(
        "Cart",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )


# ====================================
# ORDERS
# ====================================

class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    address_id = Column(
        Integer,
        ForeignKey("addresses.id")
    )

    payment_method = Column(
        String(50),
        default="online"
    )

    total_amount = Column(
        Numeric(10,2),
        nullable=False
    )

    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="orders"
    )

    address = relationship(
        "Address"
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete"
    )


# ====================================
# ORDER ITEMS
# ====================================

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey(
            "orders.id",
            ondelete="CASCADE"
        )
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    price = Column(
        Numeric(10,2),
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship(
        "Product"
    )


# ====================================
# PAYMENTS
# ====================================

class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id")
    )

    razorpay_order_id = Column(
        String(255),
        unique=True
    )

    razorpay_payment_id = Column(
        String(255),
        unique=True
    )

    amount = Column(
        Numeric(10,2),
        nullable=False
    )

    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING
    )

    payment_method = Column(
        String(50)
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    order = relationship(
        "Order",
        backref="payment"
    )