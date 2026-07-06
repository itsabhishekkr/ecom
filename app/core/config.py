import os
from dotenv import load_dotenv

load_dotenv()


def get_razorpay_key_id() -> str:
    return os.getenv("RAZORPAY_KEY_ID")


def get_razorpay_secret() -> str:
    return os.getenv("RAZORPAY_SECRET")


def get_razorpay_settings() -> dict:
    return {
        "key_id": get_razorpay_key_id(),
        "secret": get_razorpay_secret(),
    }
