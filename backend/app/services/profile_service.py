"""用户与个人中心业务逻辑。"""

import json
import random
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ApplicationStatus, ErrorCode, ExpSource
from app.core.exceptions import raise_app
from app.core.security import hash_password, verify_password
from app.models import AuthorApplication, CheckIn, ExpLog, User
from app.schemas.auth import UserOut
from app.schemas.common import PageParams, PageResult
from app.schemas.profile import (
    AuthorApplicationOut,
    CheckInOut,
    CheckInStatusOut,
    ExpLogOut,
    TitlesOut,
    TitleTierOut,
)
from app.services.title_service import get_title_info, list_all_titles
from app.utils.validators import assert_nickname_available, normalize_nickname
from app.data.fortunes import FORTUNES


def get_user_out(user: User) -> UserOut:
    info = get_title_info(user.exp)
    return UserOut(
        id=user.id,
        nickname=user.nickname,
        avatar=user.avatar or "",
        role=user.role,
        exp=user.exp,
        level=info.level,
        title=info.title,
        exp_in_level=info.exp_in_level,
        exp_to_next=info.exp_to_next,
    )


def update_profile(db: Session, user: User, nickname: str | None, avatar: str | None) -> UserOut:
    normalized = normalize_nickname(nickname)
    if normalized is not None and normalized != user.nickname:
        assert_nickname_available(db, normalized, user.id)
        user.nickname = normalized
    if avatar is not None:
        user.avatar = avatar
    db.commit()
    db.refresh(user)
    return get_user_out(user)


def change_password(db: Session, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise_app(ErrorCode.BAD_REQUEST, "原密码错误")
    user.password_hash = hash_password(new_password)
    db.commit()


def check_in_status(db: Session, user_id: int) -> CheckInStatusOut:
    today = date.today()
    record = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user_id, CheckIn.check_date == today)
        .first()
    )
    return CheckInStatusOut(
        checked_in=record is not None,
        fortune_text=record.fortune_text if record else None,
    )


def check_in(db: Session, user: User) -> CheckInOut:
    today = date.today()
    exists = (
        db.query(CheckIn)
        .filter(CheckIn.user_id == user.id, CheckIn.check_date == today)
        .first()
    )
    if exists:
        raise_app(ErrorCode.ALREADY_CHECKED_IN)

    fortune = random.choice(FORTUNES)
    gained = random.randint(5, 15)
    old_info = get_title_info(user.exp)
    db.add(
        CheckIn(
            user_id=user.id,
            fortune_text=fortune,
            exp_gained=gained,
            check_date=today,
        ),
    )
    db.add(ExpLog(user_id=user.id, source=ExpSource.CHECK_IN.value, amount=gained))
    user.exp += gained
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise_app(ErrorCode.ALREADY_CHECKED_IN)
    db.refresh(user)
    new_info = get_title_info(user.exp)
    leveled_up = new_info.level > old_info.level
    return CheckInOut(
        fortune_text=fortune,
        exp_gained=gained,
        exp=user.exp,
        leveled_up=leveled_up,
        new_title=new_info.title if leveled_up else None,
        level=new_info.level,
        title=new_info.title,
    )


def list_exp_logs(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> PageResult[ExpLogOut]:
    params = PageParams(page=max(1, page), page_size=min(max(1, page_size), 50))
    query = db.query(ExpLog).filter(ExpLog.user_id == user_id).order_by(ExpLog.created_at.desc())
    total = query.count()
    logs = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    source_map = {
        ExpSource.CHECK_IN.value: "每日签到",
        ExpSource.READ.value: "阅读",
        ExpSource.COMMENT.value: "评论",
    }
    items = [
        ExpLogOut(
            id=log.id,
            source=source_map.get(log.source, log.source),
            amount=log.amount,
            time=log.created_at.strftime("%Y-%m-%d %H:%M"),
        )
        for log in logs
    ]
    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)


def get_titles(db: Session, user_id: int) -> TitlesOut:
    user = db.get(User, user_id)
    if not user:
        raise_app(ErrorCode.NOT_FOUND, "用户不存在")
    info = get_title_info(user.exp)
    tiers = [
        TitleTierOut(**tier)
        for tier in list_all_titles(user.exp)
    ]
    return TitlesOut(
        level=info.level,
        title=info.title,
        exp=info.exp,
        exp_in_level=info.exp_in_level,
        exp_to_next=info.exp_to_next,
        progress=info.progress,
        tiers=tiers,
    )


def submit_author_application(db: Session, user: User, reason: str) -> AuthorApplicationOut:
    pending = (
        db.query(AuthorApplication)
        .filter(
            AuthorApplication.user_id == user.id,
            AuthorApplication.status == ApplicationStatus.PENDING.value,
        )
        .first()
    )
    if pending:
        raise_app(ErrorCode.CONFLICT, "已有待审核的申请")
    db.add(AuthorApplication(user_id=user.id, reason=reason))
    db.commit()
    return AuthorApplicationOut(status=ApplicationStatus.PENDING.value, reason=reason)


def get_author_application(db: Session, user_id: int) -> AuthorApplicationOut | None:
    app = (
        db.query(AuthorApplication)
        .filter(AuthorApplication.user_id == user_id)
        .order_by(AuthorApplication.created_at.desc())
        .first()
    )
    if not app:
        return None
    return AuthorApplicationOut(
        status=app.status,
        reason=app.reason,
        review_note=app.review_note,
    )


def get_reader_settings(db: Session, user_id: int) -> dict | None:
    user = db.get(User, user_id)
    if not user or not user.reader_settings:
        return None
    try:
        data = json.loads(user.reader_settings)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def update_reader_settings(db: Session, user_id: int, settings: dict) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise_app(ErrorCode.NOT_FOUND, "用户不存在")
    user.reader_settings = json.dumps(settings, ensure_ascii=False)
    db.commit()
    return settings
