"""Sends each subscriber's daily reading at their chosen local hour.

Runs every 15 minutes. For each active subscriber, if it is at or past their
notify_hour in their own time zone and today's reading hasn't been sent,
generate it and deliver it by Telegram and/or email.
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

from app.astrology.transits import transits_for
from app.config import get_settings
from app.database import SessionLocal
from app.models import BirthChart, Message, User, utcnow
from app.services import ai
from app.services.notify import send_email, send_telegram

log = logging.getLogger(__name__)


def send_due_readings() -> int:
    sent = 0
    with SessionLocal() as db:
        users = db.scalars(select(User).join(BirthChart).where(User.subscribed_until > utcnow())).all()
        for user in users:
            local_now = datetime.now(ZoneInfo(user.chart.timezone))
            if local_now.hour < user.notify_hour or user.last_daily_sent == local_now.date():
                continue
            try:
                text = ai.daily_reading(user.full_name, user.chart.data, transits_for(user.chart.data))
            except Exception:
                log.exception("Reading failed for user %s", user.id)
                continue
            db.add(Message(user_id=user.id, kind="daily", content=text))
            title = f"Your horoscope for {local_now:%A, %B %d}"
            if user.telegram_chat_id:
                send_telegram(user.telegram_chat_id, f"{title}\n\n{text}")
            if user.notify_email:
                send_email(user.email, f"{get_settings().app_name}: {title}", text)
            user.last_daily_sent = local_now.date()
            db.commit()
            sent += 1
    return sent


def start_scheduler() -> BackgroundScheduler:
    sched = BackgroundScheduler(timezone="UTC")
    sched.add_job(send_due_readings, "interval", minutes=15, id="daily_readings",
                  max_instances=1, coalesce=True)
    sched.start()
    return sched
