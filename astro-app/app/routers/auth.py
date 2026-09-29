from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import create_token, current_user, hash_password, verify_password
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import LoginIn, RegisterIn, SettingsIn, TokenOut, UserOut

router = APIRouter(prefix="/api", tags=["account"])


def user_out(u: User) -> UserOut:
    bot = get_settings().telegram_bot_username
    return UserOut(
        id=u.id, email=u.email, full_name=u.full_name,
        is_active_subscriber=u.is_active_subscriber, subscribed_until=u.subscribed_until,
        notify_hour=u.notify_hour, notify_email=u.notify_email,
        telegram_connected=bool(u.telegram_chat_id),
        telegram_link=f"https://t.me/{bot}?start={u.telegram_link_token}" if bot else None,
        has_chart=u.chart is not None,
    )


@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(400, "An account with this email already exists. Sign in instead.")
    user = User(email=email, password_hash=hash_password(data.password), full_name=data.full_name.strip())
    db.add(user)
    db.commit()
    return TokenOut(access_token=create_token(user.id))


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(400, "Email or password is incorrect.")
    return TokenOut(access_token=create_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user_out(user)


@router.patch("/me", response_model=UserOut)
def update_me(data: SettingsIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if data.notify_hour is not None:
        user.notify_hour = data.notify_hour
    if data.notify_email is not None:
        user.notify_email = data.notify_email
    db.commit()
    return user_out(user)


@router.delete("/me")
def delete_me(user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Right to erasure (GDPR): removes the account, chart, payments and messages."""
    db.delete(user)
    db.commit()
    return {"deleted": True}
