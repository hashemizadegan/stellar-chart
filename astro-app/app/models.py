import secrets
from datetime import date, datetime, timezone

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Subscription
    subscribed_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Notifications
    notify_hour: Mapped[int] = mapped_column(Integer, default=8)  # local hour for the daily reading
    notify_email: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    telegram_link_token: Mapped[str] = mapped_column(
        String(64), default=lambda: secrets.token_urlsafe(16), unique=True
    )
    last_daily_sent: Mapped[date | None] = mapped_column(Date, nullable=True)

    chart: Mapped["BirthChart | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    messages: Mapped[list["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    @property
    def is_active_subscriber(self) -> bool:
        if not self.subscribed_until:
            return False
        until = self.subscribed_until
        if until.tzinfo is None:
            until = until.replace(tzinfo=timezone.utc)
        return until > utcnow()


class BirthChart(Base):
    __tablename__ = "birth_charts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    birth_date: Mapped[date] = mapped_column(Date)
    birth_time: Mapped[str | None] = mapped_column(String(5), nullable=True)  # "HH:MM" or None if unknown
    birth_place: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(64))
    utc_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    data: Mapped[dict] = mapped_column(JSON)  # the full calculated chart
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="chart")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    provider_invoice_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount_usd: Mapped[float] = mapped_column(Float)
    pay_currency: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="waiting")
    credited: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user: Mapped[User] = relationship(back_populates="payments")


class Message(Base):
    """Daily readings and Q&A history: the person's portfolio timeline."""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))  # "daily" | "question"
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

    user: Mapped[User] = relationship(back_populates="messages")
