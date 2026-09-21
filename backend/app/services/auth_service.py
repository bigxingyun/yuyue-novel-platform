"""认证业务逻辑。"""

from datetime import UTC, datetime

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ErrorCode, KeyStatus, UserRole, UserStatus
from app.core.exceptions import raise_app
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    TOKEN_TYPE_REFRESH,
)
from app.models import RecoveryKey, RegistrationKey, User
from app.schemas.auth import AuthTokens, UserOut
from app.services.profile_service import get_user_out
from app.utils.validators import assert_nickname_available, normalize_nickname


def _user_out(user: User) -> UserOut:
    return get_user_out(user)


def _auth_tokens(user: User) -> AuthTokens:
    return AuthTokens(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user=_user_out(user),
    )


def _find_user_by_account(db: Session, account: str) -> User | None:
    user = db.query(User).filter(User.nickname == account).first()
    if user:
        return user
    if account.isdigit():
        return db.get(User, int(account))
    return None


def login(db: Session, account: str, password: str) -> AuthTokens:
    user = _find_user_by_account(db, account)
    if not user or not verify_password(password, user.password_hash):
        raise_app(ErrorCode.UNAUTHORIZED, "账号或密码错误")
    if user.status == UserStatus.BANNED.value:
        raise_app(ErrorCode.ACCOUNT_BANNED)
    return _auth_tokens(user)


def refresh(db: Session, refresh_token: str) -> AuthTokens:
    user_id = decode_token(refresh_token, TOKEN_TYPE_REFRESH)
    user = db.get(User, user_id)
    if not user:
        raise_app(ErrorCode.TOKEN_EXPIRED)
    if user.status == UserStatus.BANNED.value:
        raise_app(ErrorCode.ACCOUNT_BANNED)
    return _auth_tokens(user)


def _normalize_key(code: str) -> str:
    return code.strip().upper()


def verify_registration_key(db: Session, code: str) -> None:
    code = _normalize_key(code)
    key = db.query(RegistrationKey).filter(RegistrationKey.code == code).first()
    if not key or key.status != KeyStatus.UNUSED.value:
        raise_app(ErrorCode.REGISTRATION_KEY_INVALID)
    if key.expires_at and key.expires_at < datetime.now(UTC).replace(tzinfo=None):
        key.status = KeyStatus.EXPIRED.value
        db.commit()
        raise_app(ErrorCode.REGISTRATION_KEY_INVALID)


def _consume_registration_key(db: Session, code: str, user_id: int) -> None:
    now = datetime.now(UTC).replace(tzinfo=None)
    result = db.execute(
        update(RegistrationKey)
        .where(
            RegistrationKey.code == code,
            RegistrationKey.status == KeyStatus.UNUSED.value,
        )
        .values(status=KeyStatus.USED.value, used_by=user_id, used_at=now),
    )
    if result.rowcount != 1:
        db.rollback()
        raise_app(ErrorCode.REGISTRATION_KEY_INVALID)


def register(
    db: Session,
    registration_key: str,
    nickname: str,
    password: str,
    avatar: str | None,
) -> AuthTokens:
    registration_key = _normalize_key(registration_key)
    verify_registration_key(db, registration_key)
    nickname = normalize_nickname(nickname)
    if not nickname:
        raise_app(ErrorCode.BAD_REQUEST, "昵称不能为空")
    assert_nickname_available(db, nickname, exclude_user_id=0)

    user = User(
        nickname=nickname,
        password_hash=hash_password(password),
        avatar=avatar or f"https://api.dicebear.com/7.x/notionists/svg?seed={nickname}",
        role=UserRole.USER.value,
    )
    db.add(user)
    db.flush()

    _consume_registration_key(db, registration_key, user.id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise_app(ErrorCode.CONFLICT, "昵称已被占用")
    db.refresh(user)
    return _auth_tokens(user)


def recover_password(
    db: Session,
    account: str,
    recovery_key: str,
    new_password: str,
) -> None:
    invalid_msg = "账号或找回密钥无效"
    user = _find_user_by_account(db, account)

    recovery_key = _normalize_key(recovery_key)
    key = None
    if user:
        key = db.query(RecoveryKey).filter(
            RecoveryKey.code == recovery_key,
            RecoveryKey.user_id == user.id,
        ).first()

    if not user or not key or key.status != KeyStatus.UNUSED.value:
        raise_app(ErrorCode.REGISTRATION_KEY_INVALID, invalid_msg)
    if key.expires_at and key.expires_at < datetime.now(UTC).replace(tzinfo=None):
        key.status = KeyStatus.EXPIRED.value
        db.commit()
        raise_app(ErrorCode.REGISTRATION_KEY_INVALID, invalid_msg)

    now = datetime.now(UTC).replace(tzinfo=None)
    result = db.execute(
        update(RecoveryKey)
        .where(
            RecoveryKey.id == key.id,
            RecoveryKey.status == KeyStatus.UNUSED.value,
        )
        .values(status=KeyStatus.USED.value, used_at=now),
    )
    if result.rowcount != 1:
        db.rollback()
        raise_app(ErrorCode.REGISTRATION_KEY_INVALID, invalid_msg)

    user.password_hash = hash_password(new_password)
    db.commit()
