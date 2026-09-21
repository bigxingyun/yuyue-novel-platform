"""管理后台 — 用户管理。"""

from fastapi import APIRouter

from app.api.deps import AdminUser, DbSession, Pagination, SuperAdminUser
from app.schemas.admin import UpdateUserRoleRequest, UpdateUserStatusRequest
from app.schemas.common import ok
from app.services import admin_service

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("")
def list_users(
    db: DbSession,
    _admin: AdminUser,
    pagination: Pagination,
    keyword: str | None = None,
):
    return ok(admin_service.list_users(db, pagination, keyword))


@router.patch("/{user_id}/status")
def update_status(user_id: int, body: UpdateUserStatusRequest, db: DbSession, admin: AdminUser):
    return ok(admin_service.update_user_status(db, admin, user_id, body.status))


@router.patch("/{user_id}/role")
def update_role(
    user_id: int,
    body: UpdateUserRoleRequest,
    db: DbSession,
    _superadmin: SuperAdminUser,
):
    return ok(admin_service.update_user_role(db, _superadmin, user_id, body.role))
