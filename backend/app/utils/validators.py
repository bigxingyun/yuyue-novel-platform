"""通用字段校验。"""

from sqlalchemy.orm import Session

from app.core.constants import ErrorCode
from app.core.exceptions import raise_app
from app.models import User


def normalize_nickname(nickname: str | None) -> str | None:
    if nickname is None:
        return None
    trimmed = nickname.strip()
    return trimmed or None


def assert_nickname_available(db: Session, nickname: str, exclude_user_id: int) -> None:
    """昵称唯一性校验，排除当前用户（未改昵称时不应误判为占用）。"""
    taken = (
        db.query(User.id)
        .filter(User.nickname == nickname, User.id != exclude_user_id)
        .first()
    )
    if taken:
        raise_app(ErrorCode.NICKNAME_TAKEN)
