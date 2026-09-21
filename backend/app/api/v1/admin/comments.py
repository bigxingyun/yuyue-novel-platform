"""管理后台 — 评论审核。"""

from fastapi import APIRouter

from app.api.deps import AdminUser, DbSession, Pagination
from app.schemas.common import ok
from app.services import admin_service

router = APIRouter(prefix="/comments", tags=["admin-comments"])


@router.get("")
def list_comments(
    db: DbSession,
    _admin: AdminUser,
    pagination: Pagination,
    type: str = "chapter",
    keyword: str | None = None,
    visibility: str = "visible",
):
    return ok(
        admin_service.list_admin_comments(
            db,
            type,
            pagination.page,
            pagination.page_size,
            keyword,
            visibility,
        ),
    )


@router.post("/{comment_id}/hide")
def hide_comment(comment_id: int, db: DbSession, _admin: AdminUser, type: str):
    admin_service.hide_admin_comment(db, comment_id, type)
    return ok(None, message="已隐藏")


@router.post("/{comment_id}/unhide")
def unhide_comment(comment_id: int, db: DbSession, _admin: AdminUser, type: str):
    admin_service.unhide_admin_comment(db, comment_id, type)
    return ok(None, message="已恢复显示")
