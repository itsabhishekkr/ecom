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
