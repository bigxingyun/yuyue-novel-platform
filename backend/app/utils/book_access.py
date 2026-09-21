"""公开阅读内容访问校验。"""

from sqlalchemy.orm import Session

from app.core.constants import BookStatus, ErrorCode
from app.core.exceptions import raise_app
from app.models import Book, Chapter


def require_published_book(db: Session, book_id: int) -> Book:
    book = (
        db.query(Book)
        .filter(Book.id == book_id, Book.status == BookStatus.PUBLISHED.value)
        .first()
    )
    if not book:
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    return book


def require_published_chapter(db: Session, chapter_id: int) -> Chapter:
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise_app(ErrorCode.CHAPTER_NOT_FOUND)
    require_published_book(db, chapter.book_id)
    return chapter
