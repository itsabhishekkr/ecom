## Categories
(Admin only)
POST /categories
Request:
{
   "name":"Electronics"
}

Response:
{
   "id":1,
   "name":"Electronics"
}

GET /categories
Response:
[
   {
      "id":1,
      "name":"Electronics"
   },
   {
      "id":2,
      "name":"Clothing"
   }
]


PUT /categories/{id}

Request:
{
   "name":"Mobiles"
}

DELETE /categories/{id}

Response:
{
   "message":"Category deleted"
}


### done above all routes

Products

(Provider/Admin)

POST /products

Request:

{
   "name":"iPhone 15",
   "description":"128GB Black",
   "price":75000,
   "stock_quantity":20,
   "category_id":1,
   "image_url":"image-url"
}

Response:

{
   "id":1,
   "name":"iPhone 15",
   "price":75000
}

GET /products

Query:

/products?page=1&limit=10
/products?search=iphone
/products?category=1

Response:

{
 "total":100,
 "page":1,
 "data":[
   {
      "id":1,
      "name":"iPhone 15",
      "price":75000
   }
 ]
}

GET /products/{id}

Response:

{
   "id":1,
   "name":"iPhone 15",
   "description":"128GB",
   "price":75000,
   "stock_quantity":20
}

PUT /products/{id}

DELETE /products/{id}

Cart

POST /cart

Request:

{
   "product_id":1,
   "quantity":2
}

Response:

{
   "message":"Added to cart"
}

GET /cart

Response:

{
   "items":[
      {
         "product_id":1,
         "name":"iPhone 15",
         "quantity":2,
         "price":75000
      }
   ],
   "total":150000
}

PUT /cart/{id}

Request:

{
   "quantity":3
}

DELETE /cart/{id}
