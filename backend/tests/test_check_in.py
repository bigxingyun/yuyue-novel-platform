"""签到重复测试。"""

import uuid

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.core.security import hash_password
from app.database import SessionLocal
from app.models import CheckIn, ExpLog, User
from app.services import profile_service


def test_duplicate_check_in_returns_conflict():
    db = SessionLocal()
    nickname = f"ci_{uuid.uuid4().hex[:8]}"
    user = User(nickname=nickname, password_hash=hash_password("test123"), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)

    profile_service.check_in(db, user)

    try:
        profile_service.check_in(db, user)
        assert False, "expected AppError"
    except AppException as e:
        assert e.code == ErrorCode.ALREADY_CHECKED_IN

    # 清理：SQLite 无 AUTOINCREMENT 时会复用被删除的最大 id，
    # 若残留该用户的签到/经验行，后续复用到同一 id 的测试会被误判为「今日已签到」。
    db.query(CheckIn).filter(CheckIn.user_id == user.id).delete()
    db.query(ExpLog).filter(ExpLog.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    db.close()
