from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.astrology.chart import natal_chart
from app.astrology.geo import PlaceNotFound, geocode, local_to_utc
from app.auth import current_user
from app.config import get_settings
from app.database import get_db
from app.models import BirthChart, Message, User
from app.services import ai
from app.schemas import BirthDataIn

router = APIRouter(prefix="/api/chart", tags=["chart"])


@router.post("")
def save_birth_data(data: BirthDataIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        place = geocode(data.birth_place)
    except PlaceNotFound as e:
        raise HTTPException(400, str(e))

    time_known = data.birth_time is not None
    h, m = map(int, (data.birth_time or "12:00").split(":"))  # noon chart when time is unknown
    dt_utc = local_to_utc(data.birth_date, time(h, m), place.timezone)
    chart = natal_chart(dt_utc, place.latitude, place.longitude, time_known)

    record = user.chart or BirthChart()
    user.chart = record
    record.birth_date, record.birth_time = data.birth_date, data.birth_time
    record.birth_place = place.display_name
    record.latitude, record.longitude, record.timezone = place.latitude, place.longitude, place.timezone
    record.utc_datetime, record.data = dt_utc, chart
    # New birth data means a new chart, so any earlier report no longer applies.
    db.execute(delete(Message).where(Message.user_id == user.id, Message.kind == "natal"))
    db.commit()
    return get_chart(user)


@router.get("")
def get_chart(user: User = Depends(current_user)):
    c = user.chart
    if not c:
        raise HTTPException(404, "Add your birth details to calculate your chart.")
    return {
        "birth": {"date": c.birth_date.isoformat(), "time": c.birth_time, "place": c.birth_place,
                  "latitude": c.latitude, "longitude": c.longitude, "timezone": c.timezone,
                  "utc": c.utc_datetime.isoformat()},
        "chart": c.data,
    }


@router.get("/report")
def get_report(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """The person's general natal report. Written once per chart, then served from the database."""
    if not user.chart:
        raise HTTPException(404, "Add your birth details to get your chart report.")
    if not get_settings().free_natal_report and not user.is_active_subscriber:
        raise HTTPException(402, "Your full chart report is included with a subscription.")
    existing = db.scalar(select(Message).where(Message.user_id == user.id, Message.kind == "natal")
                         .order_by(Message.created_at.desc()))
    if existing:
        return {"content": existing.content, "created_at": existing.created_at}
    try:
        text = ai.natal_report(user.full_name, user.chart.data)
    except Exception:
        raise HTTPException(502, "Your report couldn't be written just now. Reload the page to try again.")
    msg = Message(user_id=user.id, kind="natal", content=text)
    db.add(msg)
    db.commit()
    return {"content": text, "created_at": msg.created_at}
