"""注册码原子消费测试。"""

import uuid

from app.core.constants import ErrorCode, KeyStatus
from app.core.exceptions import AppException
from app.core.security import hash_password
from app.database import SessionLocal
from app.models import RegistrationKey, User
from app.services import auth_service


def test_registration_key_cannot_be_used_twice():
    db = SessionLocal()
    code = f"YUYUE-{uuid.uuid4().hex[:8].upper()}"
    db.add(RegistrationKey(code=code, status=KeyStatus.UNUSED.value))
    db.commit()

    auth_service.register(db, code, f"reg_{uuid.uuid4().hex[:6]}", "test1234", None)

    try:
        auth_service.register(db, code, f"reg_{uuid.uuid4().hex[:6]}", "test1234", None)
        assert False, "expected AppError"
    except AppException as e:
        assert e.code == ErrorCode.REGISTRATION_KEY_INVALID

    users = db.query(User).filter(User.nickname.like("reg_%")).all()
    for u in users:
        db.delete(u)
    db.query(RegistrationKey).filter(RegistrationKey.code == code).delete()
    db.commit()
    db.close()
