"""管理后台 — 作者申请审核。"""

from fastapi import APIRouter

from app.api.deps import AdminUser, DbSession, Pagination
from app.schemas.admin import ReviewApplicationRequest
from app.schemas.common import ok
from app.services import admin_service

router = APIRouter(prefix="/applications", tags=["admin-applications"])


@router.get("")
def list_applications(
    db: DbSession,
    _admin: AdminUser,
    pagination: Pagination,
    status: str | None = None,
):
    return ok(admin_service.list_applications(db, pagination, status))


@router.patch("/{app_id}")
def review_application(
    app_id: int,
    body: ReviewApplicationRequest,
    db: DbSession,
    admin: AdminUser,
):
    return ok(
        admin_service.review_application(
            db,
            app_id,
            admin.id,
            body.status,
            body.review_note,
        ),
    )
