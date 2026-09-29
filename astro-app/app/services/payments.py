"""USDT payments through NOWPayments (https://nowpayments.io).

Flow: create invoice -> user pays on the hosted page -> NOWPayments calls
our IPN webhook -> we verify the HMAC signature -> extend the subscription.
"""
import hashlib
import hmac
import json

import httpx

from app.config import get_settings

API = "https://api.nowpayments.io/v1"


async def create_invoice(order_id: str, amount_usd: float, description: str) -> dict:
    s = get_settings()
    body = {
        "price_amount": amount_usd,
        "price_currency": "usd",
        "pay_currency": s.pay_currency,
        "order_id": order_id,
        "order_description": description,
        "ipn_callback_url": f"{s.base_url}/api/payments/ipn",
        "success_url": f"{s.base_url}/?paid=1",
        "cancel_url": f"{s.base_url}/?paid=0",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{API}/invoice", json=body, headers={"x-api-key": s.nowpayments_api_key})
        r.raise_for_status()
        return r.json()  # contains "id" and "invoice_url"


def verify_ipn(raw_body: bytes, signature: str | None) -> dict | None:
    """Return the parsed payload if the signature is valid, else None.

    NOWPayments signs the JSON body with keys sorted, using HMAC-SHA512
    and your IPN secret, and sends it in the x-nowpayments-sig header.
    """
    secret = get_settings().nowpayments_ipn_secret
    if not signature or not secret:
        return None
    payload = json.loads(raw_body)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(secret.encode(), canonical.encode(), hashlib.sha512).hexdigest()
    return payload if hmac.compare_digest(expected, signature) else None
