"""签到重复测试。"""

import uuid

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.core.security import hash_password
from app.database import SessionLocal
from app.models import User
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

    db.delete(user)
    db.commit()
    db.close()
