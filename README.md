# E-Commerce API Suite

This repository contains a fully-featured, production-ready FastAPI e-commerce backend.

## Features & Implementation
- **Authentication**: JWT-based authentication for Customers, Providers, and Admins.
- **Categories**: Full CRUD operations (Admin only) and list views for users.
- **Products**: Search, pagination, image uploads, category filtering, and provider-level permissions.
- **Cart**: Add items, update quantities with real-time stock checks, and get cart summary totals.
- **Orders**: Secure checkout, stock deduction, and historical order details tracking.
- **Address Management**: Customer address CRUD with default address support.
- **Payments**: Mock payment gateway integration (initiating transactions and status verification).
- **Dashboards**: 
  - **Provider Dashboard**: Aggregate statistics (products, orders, sales) and order fulfillment tracking.
  - **Admin Dashboard**: Global statistics (users, products, orders, revenue), user list, and account block/unblock controls.

---

## API Endpoints Reference

All authenticated endpoints require an `Authorization: Bearer <access_token>` header.

### 1. Authentication
* **POST `/auth/register`**: Register a new user. Providers start as inactive until approved by admin.
* **POST `/auth/login`**: Authenticate and retrieve JWT token.
* **POST `/auth/logout`**: Clear authentication cookies.

### 2. Categories
* **POST `/admin/categories`**: Create a category (Admin only).
* **PUT `/admin/categories/{id}`**: Update category name (Admin only).
* **DELETE `/admin/categories/{id}`**: Delete a category (Admin only).
* **GET `/com/categories`**: Fetch all categories (All authenticated users).

### 3. Products
* **POST `/products`** (and legacy `/pro/products`): Add a new product with image file upload (Provider only).
* **GET `/products`**: Retrieve paginated list of products.
  * Query parameters: `page`, `limit`, `search`, `category`.
* **GET `/products/{id}`**: Fetch product details by ID.
* **PUT `/products/{id}`**: Update product details and/or image (Provider owner or Admin).
* **DELETE `/products/{id}`**: Delete product (Provider owner or Admin).

### 4. Cart
* **POST `/cart`**: Add a product to the cart.
* **GET `/cart`**: Retrieve current cart items and total amount.
* **PUT `/cart/{cart_item_id}`**: Update item quantity.
* **DELETE `/cart/{cart_item_id}`**: Remove an item from the cart.

### 5. Address
* **POST `/address`**: Add a new shipping/billing address.
* **GET `/address`**: List all saved addresses of the current user.
* **PUT `/address/{id}`**: Update address details.
* **DELETE `/address/{id}`**: Delete address.

### 6. Orders
* **POST `/orders`**: Place an order using active cart items (deducts stock and clears cart).
* **GET `/orders`**: List all orders placed by the current user.
* **GET `/orders/{id}`**: Get detailed breakdown of a single order (including historical item prices).

### 7. Payments
* **POST `/payments/create`**: Create a payment transaction for a pending order. Returns a mock gateway URL.
* **POST `/payments/verify`**: Verify transaction status. Promotes order status to `processing`.

### 8. Provider Dashboard (Provider Only)
* **GET `/provider/dashboard`**: Fetch aggregate stats (total products, orders containing provider's products, total sales revenue).
* **GET `/provider/orders`**: Retrieve all orders containing the provider's products.
* **PUT `/provider/orders/{id}`**: Update order fulfillment status (e.g. `shipped`, `delivered`).

### 9. Admin Dashboard (Admin Only)
* **GET `/admin/dashboard`**: System-wide statistics (users, products, orders, total revenue).
* **GET `/admin/users`**: List all customer accounts.
* **GET `/admin/providers`**: List all provider accounts.
* **PUT `/admin/users/{id}`**: Toggle user `is_active` status (block/unblock/approve).

---

## Getting Started

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env` in the root folder:
   ```env
   DATABASE_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/<db_name>
   SECRET_KEY=<secret_key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Running the Server
Run the FastAPI application locally:
```bash
uvicorn app.main:app --reload
```

---

## Verification & Testing
An automated integration test script is available in the workspace. To reset the database and run the full suite:

1. Reset Database & Seed Admin:
   ```bash
   python scratch/reset_db.py
   ```
2. Run Integration Tests:
   ```bash
   python scratch/test_api.py
   ```
