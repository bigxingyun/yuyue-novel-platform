"""书籍路由。"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession, OptionalUser, Pagination
from app.schemas.comment import CreateBookCommentRequest
from app.schemas.common import ok
from app.core.constants import BOOK_CATEGORIES
from app.services import book_service, comment_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/categories")
def list_categories():
    return ok(["全部", *BOOK_CATEGORIES])


@router.get("")
def list_books(
    db: DbSession,
    pagination: Pagination,
    category: str | None = None,
    keyword: str | None = None,
    sort: str = "updated",
):
    return ok(book_service.list_books(db, pagination, category=category, keyword=keyword, sort=sort))


@router.get("/{book_id}")
def get_book(book_id: int, db: DbSession, user: OptionalUser):
    user_id = user.id if user else None
    return ok(book_service.get_book_detail(db, book_id, user_id))


@router.get("/{book_id}/update-logs")
def update_logs(book_id: int, db: DbSession):
    return ok(book_service.list_update_logs(db, book_id))


@router.get("/{book_id}/comments")
def book_comments(book_id: int, db: DbSession):
    return ok(comment_service.list_book_comments(db, book_id))


@router.post("/{book_id}/comments")
def create_book_comment(
    book_id: int,
    body: CreateBookCommentRequest,
    db: DbSession,
    user: CurrentUser,
):
    return ok(
        comment_service.create_book_comment(
            db, book_id, user.id, body.content, body.parent_id,
        ),
    )
