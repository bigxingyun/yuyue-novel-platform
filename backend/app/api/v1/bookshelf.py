"""书架路由。"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.bookshelf import AddBookshelfRequest
from app.schemas.common import ok
from app.services import bookshelf_service

router = APIRouter(prefix="/bookshelf", tags=["bookshelf"])


@router.get("")
def list_bookshelf(db: DbSession, user: CurrentUser):
    return ok(bookshelf_service.list_bookshelf(db, user.id))


@router.post("")
def add_bookshelf(body: AddBookshelfRequest, db: DbSession, user: CurrentUser):
    bookshelf_service.add_to_bookshelf(db, user.id, body.book_id)
    return ok(None, message="已加入书架")


@router.delete("/{book_id}")
def remove_bookshelf(book_id: int, db: DbSession, user: CurrentUser):
    bookshelf_service.remove_from_bookshelf(db, user.id, book_id)
    return ok(None, message="已从书架移除")
