"""书籍业务逻辑。"""

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.core.constants import BookStatus, ErrorCode
from app.core.exceptions import raise_app
from app.models import Book, BookComment, Bookshelf, Chapter, ReadingProgress, UpdateLog, User
from app.schemas.book import (
    BookCommentOut,
    BookDetailOut,
    BookListItem,
    ChapterBrief,
    ChapterOut,
    ImageBlockOut,
    ReadingProgressOut,
    TextBlockOut,
    UpdateLogOut,
)
from app.schemas.common import PageParams, PageResult
from app.utils.book_access import require_published_book
from app.utils.chapter_content import parse_chapter_blocks, split_paragraphs


def _format_date(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d")


def _relative_time(dt: datetime) -> str:
    delta = datetime.now() - dt.replace(tzinfo=None) if dt.tzinfo else datetime.now() - dt
    days = delta.days
    if days <= 0:
        return "今天"
    if days == 1:
        return "1 天前"
    if days < 7:
        return f"{days} 天前"
    if days < 30:
        return f"{days // 7} 周前"
    return _format_date(dt)


def _blocks_out(content: str) -> list[TextBlockOut | ImageBlockOut]:
    result: list[TextBlockOut | ImageBlockOut] = []
    for block in parse_chapter_blocks(content):
        if block["type"] == "text":
            result.append(
                TextBlockOut(text=block["text"], paragraph_index=block["paragraph_index"]),
            )
        else:
            result.append(
                ImageBlockOut(
                    url=block["url"],
                    after_paragraph_index=block["after_paragraph_index"],
                ),
            )
    return result


def list_books(
    db: Session,
    params: PageParams,
    *,
    category: str | None = None,
    keyword: str | None = None,
    sort: str = "updated",
) -> PageResult[BookListItem]:
    query = (
        db.query(Book)
        .join(User, Book.author_id == User.id)
        .options(joinedload(Book.author))
        .filter(Book.status == BookStatus.PUBLISHED.value)
    )

    if category and category not in ("全部", ""):
        query = query.filter(Book.category == category)
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter(or_(Book.title.ilike(kw), User.nickname.ilike(kw)))

    if sort == "words":
        query = query.order_by(Book.word_count.desc())
    else:
        query = query.order_by(Book.updated_at.desc())

    total = query.count()
    books = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()

    items = [
        BookListItem(
            id=b.id,
            title=b.title,
            author=b.author.nickname if b.author else "",
            category=b.category,
            cover=b.cover,
            word_count=b.word_count,
            updated_at=_format_date(b.updated_at),
        )
        for b in books
    ]
    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)


def get_book_detail(db: Session, book_id: int, user_id: int | None) -> BookDetailOut:
    book = (
        db.query(Book)
        .options(joinedload(Book.chapters), joinedload(Book.author))
        .filter(Book.id == book_id, Book.status == BookStatus.PUBLISHED.value)
        .first()
    )
    if not book:
        raise_app(ErrorCode.BOOK_NOT_FOUND)

    progress_out = None
    in_shelf = False
    if user_id:
        prog = (
            db.query(ReadingProgress)
            .filter(ReadingProgress.user_id == user_id, ReadingProgress.book_id == book_id)
            .first()
        )
        if prog:
            progress_out = ReadingProgressOut(chapter_id=prog.chapter_id, offset=prog.offset)
        in_shelf = (
            db.query(Bookshelf)
            .filter(Bookshelf.user_id == user_id, Bookshelf.book_id == book_id)
            .first()
            is not None
        )

    chapters = [
        ChapterBrief(id=c.id, title=c.title, word_count=c.word_count)
        for c in sorted(book.chapters, key=lambda x: x.sort_order)
    ]

    return BookDetailOut(
        id=book.id,
        title=book.title,
        author=book.author.nickname if book.author else "",
        author_id=book.author_id,
        category=book.category,
        description=book.description,
        cover=book.cover,
        word_count=book.word_count,
        updated_at=_format_date(book.updated_at),
        chapters=chapters,
        progress=progress_out,
        in_shelf=in_shelf,
    )


def get_chapter(db: Session, chapter_id: int) -> ChapterOut:
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise_app(ErrorCode.CHAPTER_NOT_FOUND)
    book = db.get(Book, chapter.book_id)
    if not book or book.status != BookStatus.PUBLISHED.value:
        raise_app(ErrorCode.CHAPTER_NOT_FOUND)

    return ChapterOut(
        id=chapter.id,
        book_id=chapter.book_id,
        title=chapter.title,
        content=chapter.content,
        paragraphs=split_paragraphs(chapter.content),
        blocks=_blocks_out(chapter.content),
        word_count=chapter.word_count,
    )


def list_update_logs(db: Session, book_id: int) -> list[UpdateLogOut]:
    require_published_book(db, book_id)
    logs = (
        db.query(UpdateLog)
        .join(Chapter, UpdateLog.chapter_id == Chapter.id)
        .filter(UpdateLog.book_id == book_id)
        .order_by(UpdateLog.created_at.desc())
        .all()
    )
    result = []
    for log in logs:
        chapter = db.get(Chapter, log.chapter_id)
        result.append(
            UpdateLogOut(
                chapter_id=log.chapter_id,
                date=_format_date(log.created_at),
                chapter_title=chapter.title if chapter else "",
                added_words=log.added_words,
            ),
        )
    return result


def list_book_comments(db: Session, book_id: int) -> list[BookCommentOut]:
    """Deprecated: 请使用 comment_service.list_book_comments（路由已迁移）。"""
    if not db.get(Book, book_id):
        raise_app(ErrorCode.BOOK_NOT_FOUND)

    comments = (
        db.query(BookComment)
        .join(User, BookComment.user_id == User.id)
        .filter(BookComment.book_id == book_id, BookComment.is_hidden.is_(False))
        .order_by(BookComment.is_pinned.desc(), BookComment.created_at.desc())
        .all()
    )
    result = []
    for c in comments:
        user = db.get(User, c.user_id)
        result.append(
            BookCommentOut(
                id=c.id,
                user=user.nickname if user else "读者",
                avatar=user.avatar if user else "",
                time=_relative_time(c.created_at),
                content=c.content,
            ),
        )
    return result


def create_book_comment(db: Session, book_id: int, user_id: int, content: str) -> BookCommentOut:
    if not db.get(Book, book_id):
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    comment = BookComment(book_id=book_id, user_id=user_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    user = db.get(User, user_id)
    return BookCommentOut(
        id=comment.id,
        user=user.nickname if user else "读者",
        avatar=user.avatar if user else "",
        time="刚刚",
        content=comment.content,
    )
