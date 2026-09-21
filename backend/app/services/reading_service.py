"""阅读进度与历史。"""

from sqlalchemy.orm import Session

from app.core.constants import BookStatus, ErrorCode
from app.core.exceptions import raise_app
from app.models import Book, Chapter, ReadingHistory, ReadingProgress
from app.schemas.book import ReadingProgressOut
from app.schemas.bookshelf import ReadingHistoryOut, UpdateProgressRequest
from app.schemas.common import PageParams, PageResult
from app.services.exp_service import award_read_exp
from app.utils.datetime_util import format_display_datetime, now_utc


def get_progress(db: Session, user_id: int, book_id: int) -> ReadingProgressOut | None:
    prog = (
        db.query(ReadingProgress)
        .filter(ReadingProgress.user_id == user_id, ReadingProgress.book_id == book_id)
        .first()
    )
    if not prog:
        return None
    return ReadingProgressOut(chapter_id=prog.chapter_id, offset=prog.offset)


def update_progress(db: Session, user_id: int, data: UpdateProgressRequest) -> ReadingProgressOut:
    book = db.get(Book, data.book_id)
    chapter = db.get(Chapter, data.chapter_id)
    if not book or book.status != BookStatus.PUBLISHED.value:
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    if not chapter or chapter.book_id != data.book_id:
        raise_app(ErrorCode.CHAPTER_NOT_FOUND)

    prog = (
        db.query(ReadingProgress)
        .filter(ReadingProgress.user_id == user_id, ReadingProgress.book_id == data.book_id)
        .first()
    )
    chapter_changed = prog is None or prog.chapter_id != data.chapter_id
    if prog:
        prog.chapter_id = data.chapter_id
        prog.offset = data.offset
        prog.updated_at = now_utc()
    else:
        prog = ReadingProgress(
            user_id=user_id,
            book_id=data.book_id,
            chapter_id=data.chapter_id,
            offset=data.offset,
        )
        db.add(prog)

    db.add(
        ReadingHistory(
            user_id=user_id,
            book_id=data.book_id,
            chapter_id=data.chapter_id,
            created_at=now_utc(),
        ),
    )
    if chapter_changed:
        award_read_exp(db, user_id)
    db.commit()
    return ReadingProgressOut(chapter_id=prog.chapter_id, offset=prog.offset)


def list_history(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
) -> PageResult[ReadingHistoryOut]:
    params = PageParams(page=max(1, page), page_size=min(max(1, page_size), 50))
    query = (
        db.query(ReadingHistory, Book, Chapter)
        .join(Book, ReadingHistory.book_id == Book.id)
        .join(Chapter, ReadingHistory.chapter_id == Chapter.id)
        .filter(
            ReadingHistory.user_id == user_id,
            Book.status == BookStatus.PUBLISHED.value,
        )
        .order_by(ReadingHistory.created_at.desc())
    )
    total = query.count()
    rows = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    items = [
        ReadingHistoryOut(
            id=row.id,
            book_id=book.id,
            chapter_id=row.chapter_id,
            title=book.title,
            cover=book.cover,
            chapter_title=chapter.title,
            read_at=format_display_datetime(row.created_at),
        )
        for row, book, chapter in rows
    ]
    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)
