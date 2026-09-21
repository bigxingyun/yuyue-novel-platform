"""书架业务逻辑。"""

from sqlalchemy.orm import Session, joinedload

from app.core.constants import BookStatus, ErrorCode
from app.core.exceptions import raise_app
from app.models import Book, Bookshelf, Chapter, ReadingProgress
from app.schemas.bookshelf import BookshelfItemOut

from app.utils.datetime_util import format_display_date, format_display_datetime


def list_bookshelf(db: Session, user_id: int) -> list[BookshelfItemOut]:
    rows = (
        db.query(Bookshelf)
        .join(Book, Bookshelf.book_id == Book.id)
        .filter(Bookshelf.user_id == user_id, Book.status == BookStatus.PUBLISHED.value)
        .all()
    )
    items = []
    for row in rows:
        book = (
            db.query(Book)
            .options(joinedload(Book.author))
            .filter(Book.id == row.book_id)
            .first()
        )
        if not book:
            continue
        author = book.author
        prog = (
            db.query(ReadingProgress)
            .filter(ReadingProgress.user_id == user_id, ReadingProgress.book_id == book.id)
            .first()
        )
        chapter_title = None
        chapter_id = None
        progress_pct = 0.0
        read_at = None
        if prog:
            chapter_id = prog.chapter_id
            progress_pct = round(prog.offset * 100)
            ch = db.get(Chapter, prog.chapter_id)
            chapter_title = ch.title if ch else None
            read_at = format_display_datetime(prog.updated_at)

        items.append(
            BookshelfItemOut(
                id=book.id,
                title=book.title,
                author=author.nickname if author else "",
                cover=book.cover,
                word_count=book.word_count,
                updated_at=format_display_date(book.updated_at),
                progress=progress_pct,
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                read_at=read_at,
            ),
        )
    items.sort(key=lambda x: x.read_at or "", reverse=True)
    return items


def add_to_bookshelf(db: Session, user_id: int, book_id: int) -> None:
    book = db.get(Book, book_id)
    if not book or book.status != BookStatus.PUBLISHED.value:
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    exists = (
        db.query(Bookshelf)
        .filter(Bookshelf.user_id == user_id, Bookshelf.book_id == book_id)
        .first()
    )
    if exists:
        return
    db.add(Bookshelf(user_id=user_id, book_id=book_id))
    db.commit()


def remove_from_bookshelf(db: Session, user_id: int, book_id: int) -> None:
    row = (
        db.query(Bookshelf)
        .filter(Bookshelf.user_id == user_id, Bookshelf.book_id == book_id)
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
