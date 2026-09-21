"""作者端业务逻辑。"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import BOOK_CATEGORIES, BookStatus, ErrorCode
from app.core.exceptions import raise_app
from app.models import Book, Chapter, UpdateLog
from app.utils.chapter_content import normalize_chapter_content, validate_chapter_content
from app.schemas.author import (
    AuthorBookOut,
    AuthorChapterDetailOut,
    AuthorChapterOut,
    CreateBookRequest,
    CreateChapterRequest,
    UpdateBookRequest,
    UpdateChapterRequest,
)


def _format_date(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d") if dt else ""


def _book_out(db: Session, book: Book) -> AuthorBookOut:
    chapter_count = db.query(Chapter).filter(Chapter.book_id == book.id).count()
    return AuthorBookOut(
        id=book.id,
        title=book.title,
        description=book.description or "",
        cover=book.cover,
        category=book.category,
        status=book.status,
        admin_delisted=bool(getattr(book, "admin_delisted", False)),
        word_count=book.word_count,
        chapter_count=chapter_count,
        updated_at=_format_date(book.updated_at),
    )


def _get_owned_book(db: Session, author_id: int, book_id: int) -> Book:
    book = db.query(Book).filter(Book.id == book_id, Book.author_id == author_id).first()
    if not book:
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    return book


def list_author_books(db: Session, author_id: int) -> list[AuthorBookOut]:
    books = db.query(Book).filter(Book.author_id == author_id).order_by(Book.updated_at.desc()).all()
    return [_book_out(db, b) for b in books]


def create_book(db: Session, author_id: int, data: CreateBookRequest) -> AuthorBookOut:
    category = data.category if data.category in BOOK_CATEGORIES else "其他"
    book = Book(
        title=data.title,
        author_id=author_id,
        description=data.description,
        category=category,
        cover=data.cover or f"https://picsum.photos/seed/book-{author_id}-{data.title}/400/560",
        status=BookStatus.DRAFT.value,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return _book_out(db, book)


def update_book(db: Session, author_id: int, book_id: int, data: UpdateBookRequest) -> AuthorBookOut:
    book = _get_owned_book(db, author_id, book_id)
    if data.title is not None:
        book.title = data.title
    if data.description is not None:
        book.description = data.description
    if data.category is not None:
        book.category = data.category if data.category in BOOK_CATEGORIES else book.category
    if data.cover is not None:
        book.cover = data.cover
    db.commit()
    db.refresh(book)
    return _book_out(db, book)


def _count_words(content: str) -> int:
    return len(content.replace("\n", "").replace(" ", ""))


def _recalc_book_word_count(db: Session, book: Book) -> None:
    total = (
        db.query(func.coalesce(func.sum(Chapter.word_count), 0))
        .filter(Chapter.book_id == book.id)
        .scalar()
    )
    book.word_count = int(total or 0)


def _chapter_out(chapter: Chapter) -> AuthorChapterOut:
    return AuthorChapterOut(
        id=chapter.id,
        title=chapter.title,
        word_count=chapter.word_count,
        sort_order=chapter.sort_order,
        updated_at=_format_date(chapter.updated_at),
    )


def _get_owned_chapter(db: Session, author_id: int, chapter_id: int) -> Chapter:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise_app(ErrorCode.CHAPTER_NOT_FOUND)
    _get_owned_book(db, author_id, chapter.book_id)
    return chapter


def _maybe_add_update_log(db: Session, book: Book, chapter: Chapter, added_words: int) -> None:
    if book.status != BookStatus.PUBLISHED.value or added_words <= 0:
        return
    db.add(
        UpdateLog(
            book_id=book.id,
            chapter_id=chapter.id,
            added_words=added_words,
        ),
    )


def get_chapter(db: Session, author_id: int, chapter_id: int) -> AuthorChapterDetailOut:
    chapter = _get_owned_chapter(db, author_id, chapter_id)
    return AuthorChapterDetailOut(
        id=chapter.id,
        title=chapter.title,
        content=chapter.content,
        word_count=chapter.word_count,
        sort_order=chapter.sort_order,
        updated_at=_format_date(chapter.updated_at),
    )


def list_chapters(db: Session, author_id: int, book_id: int) -> list[AuthorChapterOut]:
    _get_owned_book(db, author_id, book_id)
    chapters = (
        db.query(Chapter)
        .filter(Chapter.book_id == book_id)
        .order_by(Chapter.sort_order, Chapter.id)
        .all()
    )
    return [_chapter_out(c) for c in chapters]


def create_chapter(
    db: Session,
    author_id: int,
    book_id: int,
    data: CreateChapterRequest,
) -> AuthorChapterOut:
    book = _get_owned_book(db, author_id, book_id)
    max_order = (
        db.query(func.max(Chapter.sort_order)).filter(Chapter.book_id == book_id).scalar()
    ) or 0
    validate_chapter_content(data.content)
    content = normalize_chapter_content(data.content)
    word_count = _count_words(content)
    chapter = Chapter(
        book_id=book_id,
        title=data.title,
        content=content,
        word_count=word_count,
        sort_order=max_order + 1,
    )
    db.add(chapter)
    db.flush()
    _recalc_book_word_count(db, book)
    _maybe_add_update_log(db, book, chapter, word_count)
    db.commit()
    db.refresh(chapter)
    return _chapter_out(chapter)


def update_chapter(
    db: Session,
    author_id: int,
    chapter_id: int,
    data: UpdateChapterRequest,
) -> AuthorChapterOut:
    chapter = _get_owned_chapter(db, author_id, chapter_id)
    book = db.get(Book, chapter.book_id)
    old_words = chapter.word_count
    if data.title is not None:
        chapter.title = data.title
    if data.content is not None:
        validate_chapter_content(data.content)
        chapter.content = normalize_chapter_content(data.content)
        chapter.word_count = _count_words(chapter.content)
    db.flush()
    if book:
        _recalc_book_word_count(db, book)
        added = max(0, chapter.word_count - old_words)
        _maybe_add_update_log(db, book, chapter, added)
    db.commit()
    db.refresh(chapter)
    return _chapter_out(chapter)


def delete_chapter(db: Session, author_id: int, chapter_id: int) -> None:
    chapter = _get_owned_chapter(db, author_id, chapter_id)
    book = db.get(Book, chapter.book_id)
    db.delete(chapter)
    db.flush()
    if book:
        _recalc_book_word_count(db, book)
    db.commit()


def reorder_chapters(db: Session, author_id: int, book_id: int, chapter_ids: list[int]) -> list[AuthorChapterOut]:
    book = _get_owned_book(db, author_id, book_id)
    chapters = db.query(Chapter).filter(Chapter.book_id == book_id).all()
    id_map = {c.id: c for c in chapters}
    if set(chapter_ids) != set(id_map.keys()):
        raise_app(ErrorCode.BAD_REQUEST, "章节列表不完整")
    for idx, cid in enumerate(chapter_ids):
        id_map[cid].sort_order = idx + 1
    db.commit()
    return list_chapters(db, author_id, book.id)


def publish_book(db: Session, author_id: int, book_id: int) -> AuthorBookOut:
    book = _get_owned_book(db, author_id, book_id)
    if book.status == BookStatus.UNPUBLISHED.value and book.admin_delisted:
        raise_app(ErrorCode.BAD_REQUEST, "作品已被管理员下架，修改后请联系管理员审核上架")
    chapter_count = db.query(Chapter).filter(Chapter.book_id == book.id).count()
    if chapter_count == 0:
        raise_app(ErrorCode.BAD_REQUEST, "至少需要一个章节才能发布")
    was_published = book.status == BookStatus.PUBLISHED.value
    book.status = BookStatus.PUBLISHED.value
    if not was_published:
        latest = (
            db.query(Chapter)
            .filter(Chapter.book_id == book.id)
            .order_by(Chapter.sort_order.desc(), Chapter.id.desc())
            .first()
        )
        if latest:
            _maybe_add_update_log(db, book, latest, latest.word_count)
    db.commit()
    db.refresh(book)
    return _book_out(db, book)


def unpublish_book(db: Session, author_id: int, book_id: int) -> AuthorBookOut:
    book = _get_owned_book(db, author_id, book_id)
    if book.admin_delisted:
        raise_app(ErrorCode.BAD_REQUEST, "作品已被管理员下架，请联系管理员审核上架")
    if book.status != BookStatus.PUBLISHED.value:
        raise_app(ErrorCode.BAD_REQUEST, "仅已发布作品可下架")
    book.status = BookStatus.UNPUBLISHED.value
    db.commit()
    db.refresh(book)
    return _book_out(db, book)


def delete_book(db: Session, author_id: int, book_id: int) -> None:
    book = _get_owned_book(db, author_id, book_id)
    if book.status != BookStatus.DRAFT.value:
        raise_app(ErrorCode.BAD_REQUEST, "仅草稿状态可删除")
    db.delete(book)
    db.commit()
