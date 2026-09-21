"""管理后台 — 密钥管理。"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import AdminUser, DbSession, Pagination
from app.schemas.admin import GenerateKeysRequest
from app.schemas.common import ok
from app.services import admin_service

router = APIRouter(prefix="/keys", tags=["admin-keys"])


class RecoveryKeyRequest(BaseModel):
    user_id: int = Field(ge=1)


@router.post("/registration")
def generate_registration_keys(body: GenerateKeysRequest, db: DbSession, admin: AdminUser):
    return ok(admin_service.generate_registration_keys(db, admin.id, body.count, body.expire_days))


@router.get("/registration")
def list_registration_keys(db: DbSession, _admin: AdminUser, pagination: Pagination):
    return ok(admin_service.list_registration_keys(db, pagination))


@router.post("/recovery")
def generate_recovery_key(body: RecoveryKeyRequest, db: DbSession, admin: AdminUser):
    return ok(admin_service.generate_recovery_key(db, admin.id, body.user_id))
