"""认证路由。"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import (
    AuthTokens,
    LoginRequest,
    RecoverRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterVerifyRequest,
)
from app.schemas.common import ok
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(body: LoginRequest, db: DbSession):
    return ok(auth_service.login(db, body.account, body.password))


@router.post("/refresh")
def refresh(body: RefreshRequest, db: DbSession):
    return ok(auth_service.refresh(db, body.refresh_token))


@router.post("/register/verify")
def verify_register(body: RegisterVerifyRequest, db: DbSession):
    auth_service.verify_registration_key(db, body.registration_key)
    return ok({"valid": True})


@router.post("/register")
def register(body: RegisterRequest, db: DbSession):
    return ok(
        auth_service.register(
            db,
            body.registration_key,
            body.nickname,
            body.password,
            body.avatar,
        ),
    )


@router.post("/recover")
def recover(body: RecoverRequest, db: DbSession):
    auth_service.recover_password(db, body.account, body.recovery_key, body.new_password)
    return ok(None, message="密码已重置")


@router.post("/logout")
def logout(_user: CurrentUser):
    return ok(None, message="已登出")
