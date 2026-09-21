"""阅读进度路由。"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.bookshelf import UpdateProgressRequest
from app.schemas.common import ok
from app.services import reading_service

router = APIRouter(prefix="/reading", tags=["reading"])


@router.get("/progress/{book_id}")
def get_progress(book_id: int, db: DbSession, user: CurrentUser):
    return ok(reading_service.get_progress(db, user.id, book_id))


@router.put("/progress")
def update_progress(body: UpdateProgressRequest, db: DbSession, user: CurrentUser):
    return ok(reading_service.update_progress(db, user.id, body))


@router.get("/history")
def list_history(db: DbSession, user: CurrentUser, page: int = 1, page_size: int = 20):
    return ok(reading_service.list_history(db, user.id, page, page_size))
