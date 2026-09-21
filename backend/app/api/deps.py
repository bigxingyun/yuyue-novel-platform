"""路由依赖注入。"""

from collections.abc import Callable, Generator
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, ErrorCode, UserRole, UserStatus
from app.core.exceptions import raise_app
from app.core.security import try_decode_token, TOKEN_TYPE_ACCESS
from app.database import get_db
from app.models import User
from app.schemas.common import PageParams

DbSession = Annotated[Session, Depends(get_db)]

ADMIN_ROLES = {UserRole.ADMIN.value, UserRole.SUPERADMIN.value}


def get_pagination(
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> PageParams:
    if page < 1:
        raise_app(ErrorCode.BAD_REQUEST, "page 必须 >= 1")
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise_app(ErrorCode.BAD_REQUEST, f"page_size 必须在 1–{MAX_PAGE_SIZE} 之间")
    return PageParams(page=page, page_size=page_size)


Pagination = Annotated[PageParams, Depends(get_pagination)]


def _user_from_token(authorization: str | None, db: Session) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        return None
    user_id = try_decode_token(token, TOKEN_TYPE_ACCESS)
    if user_id is None:
        return None
    user = db.get(User, user_id)
    if not user:
        raise_app(ErrorCode.UNAUTHORIZED)
    if user.status == UserStatus.BANNED.value:
        raise_app(ErrorCode.ACCOUNT_BANNED)
    return user


def get_current_user(
    db: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    user = _user_from_token(authorization, db)
    if not user:
        raise_app(ErrorCode.UNAUTHORIZED)
    return user


def get_current_user_optional(
    db: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User | None:
    return _user_from_token(authorization, db)


def require_roles(*roles: UserRole) -> Callable[..., User]:
    allowed = {r.value for r in roles}

    def _dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in allowed:
            if UserRole.ADMIN in roles or UserRole.SUPERADMIN in roles:
                raise_app(ErrorCode.ADMIN_REQUIRED)
            raise_app(ErrorCode.AUTHOR_REQUIRED)
        return user

    return _dependency


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in ADMIN_ROLES:
        raise_app(ErrorCode.ADMIN_REQUIRED)
    return user


def require_superadmin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != UserRole.SUPERADMIN.value:
        raise_app(ErrorCode.ADMIN_REQUIRED, "需要超级管理员权限")
    return user


def require_author(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in {UserRole.AUTHOR.value, UserRole.ADMIN.value, UserRole.SUPERADMIN.value}:
        raise_app(ErrorCode.AUTHOR_REQUIRED)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
AdminUser = Annotated[User, Depends(require_admin)]
SuperAdminUser = Annotated[User, Depends(require_superadmin)]
AuthorUser = Annotated[User, Depends(require_author)]