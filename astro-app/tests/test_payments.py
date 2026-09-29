import hashlib
import hmac
import json

from app.config import get_settings
from app.services.payments import verify_ipn


def test_ipn_signature(monkeypatch):
    monkeypatch.setattr(get_settings(), "nowpayments_ipn_secret", "secret123")
    payload = {"payment_status": "finished", "order_id": "sub-1-abc", "price_amount": 9.99}
    sig = hmac.new(b"secret123", json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(),
                   hashlib.sha512).hexdigest()
    assert verify_ipn(json.dumps(payload).encode(), sig) == payload
    assert verify_ipn(json.dumps(payload).encode(), "bad") is None
