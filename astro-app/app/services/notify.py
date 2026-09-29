import logging
import smtplib
from email.message import EmailMessage

import httpx

from app.config import get_settings

log = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    s = get_settings()
    if not s.smtp_host:
        return False
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = s.smtp_from or s.smtp_user, to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=20) as smtp:
            smtp.starttls()
            if s.smtp_user:
                smtp.login(s.smtp_user, s.smtp_password)
            smtp.send_message(msg)
        return True
    except Exception:
        log.exception("Email to %s failed", to)
        return False


def send_telegram(chat_id: str, text: str) -> bool:
    token = get_settings().telegram_bot_token
    if not token or not chat_id:
        return False
    try:
        r = httpx.post(f"https://api.telegram.org/bot{token}/sendMessage",
                       json={"chat_id": chat_id, "text": text}, timeout=20)
        return r.status_code == 200
    except Exception:
        log.exception("Telegram message to %s failed", chat_id)
        return False
