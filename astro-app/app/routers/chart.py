from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.astrology.chart import natal_chart
from app.astrology.geo import PlaceNotFound, geocode, local_to_utc
from app.auth import current_user
from app.database import get_db
from app.models import BirthChart, User
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
