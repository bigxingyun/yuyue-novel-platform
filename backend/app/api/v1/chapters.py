"""章节路由。"""

from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.common import ok
from app.services import book_service

router = APIRouter(prefix="/chapters", tags=["chapters"])


@router.get("/{chapter_id}")
def get_chapter(chapter_id: int, db: DbSession):
    return ok(book_service.get_chapter(db, chapter_id))
