"""Telegram bot webhook. Users connect via https://t.me/<bot>?start=<their link token>.

Register the webhook once:
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<BASE_URL>/api/telegram/webhook&secret_token=<TELEGRAM_WEBHOOK_SECRET>"
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.services.notify import send_telegram

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    secret = get_settings().telegram_webhook_secret
    if not secret or request.headers.get("x-telegram-bot-api-secret-token") != secret:
        raise HTTPException(401, "Invalid secret")
    update = await request.json()
    msg = update.get("message") or {}
    text, chat_id = msg.get("text", ""), str(msg.get("chat", {}).get("id", ""))
    if text.startswith("/start") and chat_id:
        parts = text.split(maxsplit=1)
        user = db.scalar(select(User).where(User.telegram_link_token == parts[1])) if len(parts) == 2 else None
        if user:
            user.telegram_chat_id = chat_id
            db.commit()
            send_telegram(chat_id, f"Connected, {user.full_name}. Your daily horoscope will arrive here.")
        else:
            send_telegram(chat_id, "Open the Telegram link from your account page to connect.")
    return {"ok": True}
