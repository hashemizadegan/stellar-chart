from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.astrology.transits import transits_for
from app.auth import subscriber
from app.config import get_settings
from app.database import get_db
from app.models import Message, User
from app.schemas import MessageOut, QuestionIn
from app.services import ai

router = APIRouter(prefix="/api", tags=["readings"])


def _require_chart(user: User):
    if not user.chart:
        raise HTTPException(400, "Add your birth details first.")
    return user.chart


@router.get("/today")
def today(user: User = Depends(subscriber), db: Session = Depends(get_db)):
    """Returns today's reading, generating it if the scheduler hasn't yet."""
    chart = _require_chart(user)
    tz = ZoneInfo(chart.timezone)
    local_midnight = datetime.combine(datetime.now(tz).date(), time.min, tz).astimezone(timezone.utc)
    existing = db.scalar(select(Message).where(Message.user_id == user.id, Message.kind == "daily",
                                               Message.created_at >= local_midnight)
                         .order_by(Message.created_at.desc()))
    if existing:
        return {"content": existing.content, "created_at": existing.created_at}
    transits = transits_for(chart.data)
    text = ai.daily_reading(user.full_name, chart.data, transits)
    msg = Message(user_id=user.id, kind="daily", content=text)
    db.add(msg)
    db.commit()
    return {"content": text, "created_at": msg.created_at, "transits": transits["transits"]}


@router.post("/ask", response_model=MessageOut)
def ask(data: QuestionIn, user: User = Depends(subscriber), db: Session = Depends(get_db)):
    chart = _require_chart(user)
    since = datetime.now(timezone.utc) - timedelta(days=1)
    used = db.scalar(select(func.count()).select_from(Message).where(
        Message.user_id == user.id, Message.kind == "question", Message.created_at >= since))
    limit = get_settings().questions_per_day
    if used >= limit:
        raise HTTPException(429, f"You've used your {limit} questions for today. More are available tomorrow.")

    past = db.scalars(select(Message).where(Message.user_id == user.id, Message.kind == "question")
                      .order_by(Message.created_at.desc()).limit(3)).all()
    history = [{"question": m.question, "answer": m.content} for m in reversed(past)]
    answer = ai.answer_question(user.full_name, chart.data, transits_for(chart.data), data.question, history)
    msg = Message(user_id=user.id, kind="question", question=data.question, content=answer)
    db.add(msg)
    db.commit()
    return MessageOut(id=msg.id, kind=msg.kind, question=msg.question, content=msg.content,
                      created_at=msg.created_at)


@router.get("/messages", response_model=list[MessageOut])
def messages(user: User = Depends(subscriber), db: Session = Depends(get_db)):
    rows = db.scalars(select(Message).where(Message.user_id == user.id)
                      .order_by(Message.created_at.desc()).limit(50)).all()
    return [MessageOut(id=m.id, kind=m.kind, question=m.question, content=m.content,
                       created_at=m.created_at) for m in rows]
