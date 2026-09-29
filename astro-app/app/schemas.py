from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BirthDataIn(BaseModel):
    birth_date: date
    birth_time: str | None = Field(default=None, description="HH:MM, 24h. Leave empty if unknown.")
    birth_place: str = Field(min_length=2, max_length=255)

    @field_validator("birth_time")
    @classmethod
    def check_time(cls, v: str | None) -> str | None:
        if v in (None, ""):
            return None
        try:
            hh, mm = v.split(":")[:2]
            h, m = int(hh), int(mm)
        except ValueError:
            raise ValueError("Birth time must look like 14:30.")
        if not (0 <= h < 24 and 0 <= m < 60):
            raise ValueError("Birth time must look like 14:30.")
        return f"{h:02d}:{m:02d}"


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_active_subscriber: bool
    subscribed_until: datetime | None
    notify_hour: int
    notify_email: bool
    telegram_connected: bool
    telegram_link: str | None
    has_chart: bool


class SettingsIn(BaseModel):
    notify_hour: int | None = Field(default=None, ge=0, le=23)
    notify_email: bool | None = None


class QuestionIn(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class MessageOut(BaseModel):
    id: int
    kind: str
    question: str | None
    content: str
    created_at: datetime
