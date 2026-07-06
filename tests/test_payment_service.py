import asyncio
from types import SimpleNamespace

from app.services import paymentServices


class FakeDB:
    def __init__(self, order):
        self.order = order
        self.added = []
        self.committed = False
        self.rolled_back = False

    def query(self, model):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.order

    def add(self, obj):
        self.added.append(obj)
        if not getattr(obj, "id", None):
            obj.id = 7

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def test_create_payment_returns_razorpay_checkout_details(monkeypatch):
    order = SimpleNamespace(id=1, total_amount=2500, status="pending")
    db = FakeDB(order)
    current_user = SimpleNamespace(id=42)

    async def fake_create_razorpay_order(*args, **kwargs):
        return {
            "id": "order_123",
            "amount": 250000,
            "currency": "INR",
            "receipt": "order-1",
        }

    monkeypatch.setattr(paymentServices, "create_razorpay_order", fake_create_razorpay_order, raising=False)

    result = asyncio.run(paymentServices.create_payment(db, current_user, order.id))

    assert result["payment_id"] == "7"
    assert result["razorpay_order_id"] == "order_123"
    assert result["amount"] == 2500
    assert result["currency"] == "INR"
    assert result["key_id"] == "rzp_test_TAC2dQPxFpAAVl"
