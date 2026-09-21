"""管理后台 — 章节内容管理。"""

from fastapi import APIRouter

from app.api.deps import AdminUser, DbSession
from app.schemas.admin import AdminUpdateChapterRequest
from app.schemas.common import ok
from app.services import admin_service

router = APIRouter(prefix="/chapters", tags=["admin-chapters"])


@router.get("/by-book/{book_id}")
def list_chapters(book_id: int, db: DbSession, _admin: AdminUser):
    return ok(admin_service.list_admin_chapters(db, book_id))


@router.get("/{chapter_id}")
def get_chapter(chapter_id: int, db: DbSession, _admin: AdminUser):
    return ok(admin_service.get_admin_chapter(db, chapter_id))


@router.patch("/{chapter_id}")
def update_chapter(
    chapter_id: int,
    body: AdminUpdateChapterRequest,
    db: DbSession,
    _admin: AdminUser,
):
    return ok(admin_service.update_admin_chapter(db, chapter_id, body))
