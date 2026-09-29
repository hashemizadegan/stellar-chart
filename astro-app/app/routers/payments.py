import logging
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import current_user
from app.config import get_settings
from app.database import get_db
from app.models import Payment, User, utcnow
from app.services.payments import create_invoice, verify_ipn

router = APIRouter(prefix="/api/payments", tags=["payments"])
log = logging.getLogger(__name__)


@router.post("/subscribe")
async def subscribe(user: User = Depends(current_user), db: Session = Depends(get_db)):
    s = get_settings()
    if not s.nowpayments_api_key:
        raise HTTPException(503, "Payments are not configured yet.")
    order_id = f"sub-{user.id}-{secrets.token_hex(6)}"
    try:
        inv = await create_invoice(order_id, s.subscription_price_usd,
                                   f"{s.app_name}: {s.subscription_days}-day subscription")
    except Exception:
        log.exception("Invoice creation failed")
        raise HTTPException(502, "Could not create the payment. Try again in a minute.")
    db.add(Payment(user_id=user.id, order_id=order_id, provider_invoice_id=str(inv.get("id")),
                   amount_usd=s.subscription_price_usd, pay_currency=s.pay_currency))
    db.commit()
    return {"invoice_url": inv["invoice_url"], "order_id": order_id}


@router.post("/ipn")
async def ipn(request: Request, db: Session = Depends(get_db)):
    """Webhook called by NOWPayments whenever a payment status changes."""
    payload = verify_ipn(await request.body(), request.headers.get("x-nowpayments-sig"))
    if payload is None:
        raise HTTPException(401, "Invalid signature")

    payment = db.scalar(select(Payment).where(Payment.order_id == str(payload.get("order_id"))))
    if not payment:
        return {"ok": True}  # unknown order; acknowledge so it isn't retried forever

    payment.status = payload.get("payment_status", payment.status)
    # "finished" = funds received in full. Credit only once (webhooks can repeat).
    if payment.status == "finished" and not payment.credited:
        user = payment.user
        start = user.subscribed_until if user.is_active_subscriber else utcnow()
        user.subscribed_until = start + timedelta(days=get_settings().subscription_days)
        payment.credited = True
        log.info("Subscription extended for user %s until %s", user.id, user.subscribed_until)
    db.commit()
    return {"ok": True}


@router.get("/history")
def history(user: User = Depends(current_user)):
    return [{"order_id": p.order_id, "amount_usd": p.amount_usd, "currency": p.pay_currency,
             "status": p.status, "created_at": p.created_at} for p in user.payments]
