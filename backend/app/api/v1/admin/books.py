"""管理后台 — 书籍管理。"""

from fastapi import APIRouter

from app.api.deps import AdminUser, DbSession, Pagination
from app.schemas.admin import UpdateBookStatusRequest
from app.schemas.common import ok
from app.services import admin_service

router = APIRouter(prefix="/books", tags=["admin-books"])


@router.get("")
def list_books(db: DbSession, _admin: AdminUser, pagination: Pagination):
    return ok(admin_service.list_admin_books(db, pagination))


@router.patch("/{book_id}/status")
def update_status(book_id: int, body: UpdateBookStatusRequest, db: DbSession, _admin: AdminUser):
    return ok(admin_service.update_admin_book_status(db, book_id, body.status))


@router.delete("/{book_id}")
def delete_book(book_id: int, db: DbSession, _admin: AdminUser):
    admin_service.delete_admin_book(db, book_id)
    return ok(None, message="已删除")
