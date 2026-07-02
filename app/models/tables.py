
# fastapi ->ORM(Object relational mapping) Sqlachemy->  database(store) 

# fastapi -> create engine -> ORM(translate python code to sql) -> psycopg2 Driver
# (send SQL to MySQL) 

# update in the database -> session.commit() -> commit the changes to the database
from sqlalchemy import Column, Integer, String, Text,Float, Boolean, Numeric,ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.models.dataConfig import Base

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PROVIDER = "provider"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100),unique=True,index=True,nullable=False)
    phone = Column(String(20))
    password_hash = Column(String,nullable=False)
    role = Column(Enum(UserRole),default=UserRole.CUSTOMER)
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime,server_default=func.now())

    # Relationships
    addresses = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete"
    )

    orders = relationship(
        "Order",
        back_populates="user"
    )

    products = relationship(
        "Product",
        back_populates="provider"
    )



class Address(Base):
    __tablename__ = "addresses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
        ,autoincrement=True
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


# ==========================
# CATEGORIES
# ==========================

class Category(Base):
    __tablename__ = "categories"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    name = Column(
        String(100),
        unique=True
    )

    products = relationship(
        "Product",
        back_populates="category"
    )


# ==========================
# PRODUCTS
# ==========================

class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
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

    category_id = Column(
        Integer,
        ForeignKey("categories.id")
    )

    # service provider/seller
    provider_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    category = relationship(
        "Category",
        back_populates="products"
    )

    provider = relationship(
        "User",
        back_populates="products"
    )


# ==========================
# CART
# ==========================

class Cart(Base):
    __tablename__ = "carts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete"
    )


# ==========================
# CART ITEMS
# ==========================

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    cart_id = Column(
        Integer,
        ForeignKey("carts.id")
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


# ==========================
# ORDERS
# ==========================

class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    total_amount = Column(
        Numeric(10,2)
    )

    status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="orders"
    )