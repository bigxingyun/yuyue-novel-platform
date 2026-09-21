"""经验值奖励。"""

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import ExpSource
from app.models import ExpLog, User

READ_EXP_PER_CHAPTER = 2
READ_EXP_DAILY_CAP = 20
COMMENT_EXP_PER = 5
COMMENT_EXP_DAILY_CAP = 25


def _today_start() -> datetime:
    return datetime.combine(date.today(), datetime.min.time())


def _today_exp_total(db: Session, user_id: int, source: ExpSource) -> int:
    total = (
        db.query(func.coalesce(func.sum(ExpLog.amount), 0))
        .filter(
            ExpLog.user_id == user_id,
            ExpLog.source == source.value,
            ExpLog.created_at >= _today_start(),
        )
        .scalar()
    )
    return int(total or 0)


def award_exp(db: Session, user_id: int, source: ExpSource, amount: int, daily_cap: int) -> int:
    """发放经验，返回实际发放数量（受每日上限约束）。"""
    if amount <= 0:
        return 0

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .with_for_update()
        .first()
    )
    if not user:
        return 0

    earned_today = _today_exp_total(db, user_id, source)
    if earned_today >= daily_cap:
        return 0

    actual = min(amount, daily_cap - earned_today)
    user.exp += actual
    db.add(ExpLog(user_id=user_id, source=source.value, amount=actual))
    return actual


def award_read_exp(db: Session, user_id: int) -> int:
    return award_exp(db, user_id, ExpSource.READ, READ_EXP_PER_CHAPTER, READ_EXP_DAILY_CAP)


def award_comment_exp(db: Session, user_id: int) -> int:
    return award_exp(db, user_id, ExpSource.COMMENT, COMMENT_EXP_PER, COMMENT_EXP_DAILY_CAP)

