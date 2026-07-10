import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import razorpay
load_dotenv()

RAZORPAY_KEY_ID=os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET=os.getenv("RAZORPAY_SECRET")

print(RAZORPAY_KEY_ID)
print(RAZORPAY_SECRET)

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))
print(client)

try:
    order = client.order.create({
        "amount": 100,      # ₹1.00 (100 paise)
        "currency": "INR"
    })

    print("✅ Connected Successfully")
    print(order)

except Exception as e:
    print("❌ Error")
    print(type(e))
    print(e)