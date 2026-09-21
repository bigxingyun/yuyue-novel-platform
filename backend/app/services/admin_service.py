"""管理后台业务逻辑。"""

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, update
from sqlalchemy.orm import Session

from app.core.constants import ApplicationStatus, BookStatus, CommentType, ErrorCode, KeyStatus, UserRole, UserStatus
from app.core.exceptions import raise_app
from app.models import (
    AuthorApplication,
    Book,
    BookComment,
    Bookshelf,
    Chapter,
    ChapterComment,
    ParagraphComment,
    ReadingHistory,
    ReadingProgress,
    RegistrationKey,
    RecoveryKey,
    UpdateLog,
    User,
)
from app.schemas.admin import (
    AdminBookOut,
    AdminChapterDetailOut,
    AdminChapterOut,
    AdminCommentOut,
    AdminUpdateChapterRequest,
    AdminUserOut,
    AuthorApplicationAdminOut,
    RecoveryKeyOut,
    RegistrationKeyOut,
)
from app.schemas.common import PageParams, PageResult
from app.services import comment_service
from app.utils.avatar import resolve_avatar
from app.utils.chapter_content import normalize_chapter_content, validate_chapter_content


def _format_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M")


def _gen_key(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(8).upper()}"


def list_users(
    db: Session,
    params: PageParams,
    keyword: str | None = None,
) -> PageResult[AdminUserOut]:
    query = db.query(User)
    kw = keyword.strip() if keyword else ""
    if kw:
        if kw.isdigit():
            query = query.filter(or_(User.nickname.ilike(f"%{kw}%"), User.id == int(kw)))
        else:
            query = query.filter(User.nickname.ilike(f"%{kw}%"))
    query = query.order_by(User.created_at.desc())
    total = query.count()
    users = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    items = [
        AdminUserOut(
            id=u.id,
            nickname=u.nickname,
            role=u.role,
            status=u.status,
            exp=u.exp,
            created_at=_format_dt(u.created_at),
        )
        for u in users
    ]
    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)


def update_user_status(db: Session, actor: User, user_id: int, status: str) -> AdminUserOut:
    if actor.id == user_id and status == UserStatus.BANNED.value:
        raise_app(ErrorCode.BAD_REQUEST, "不能封禁自己的账号")
    user = db.get(User, user_id)
    if not user:
        raise_app(ErrorCode.NOT_FOUND, "用户不存在")
    if user.role in {UserRole.ADMIN.value, UserRole.SUPERADMIN.value}:
        if actor.role != UserRole.SUPERADMIN.value:
            raise_app(ErrorCode.FORBIDDEN, "无权修改管理员账号")
    user.status = status
    db.commit()
    db.refresh(user)
    return AdminUserOut(
        id=user.id,
        nickname=user.nickname,
        role=user.role,
        status=user.status,
        exp=user.exp,
        created_at=_format_dt(user.created_at),
    )


def update_user_role(db: Session, actor: User, user_id: int, role: str) -> AdminUserOut:
    valid = {r.value for r in UserRole}
    if role not in valid:
        raise_app(ErrorCode.BAD_REQUEST, "无效角色")
    user = db.get(User, user_id)
    if not user:
        raise_app(ErrorCode.NOT_FOUND, "用户不存在")
    if user.role in {UserRole.ADMIN.value, UserRole.SUPERADMIN.value}:
        if actor.role != UserRole.SUPERADMIN.value:
            raise_app(ErrorCode.FORBIDDEN, "无权修改管理员角色")
    if role in {UserRole.ADMIN.value, UserRole.SUPERADMIN.value}:
        if actor.role != UserRole.SUPERADMIN.value:
            raise_app(ErrorCode.FORBIDDEN, "仅超级管理员可授予管理员权限")
    user.role = role
    db.commit()
    db.refresh(user)
    return AdminUserOut(
        id=user.id,
        nickname=user.nickname,
        role=user.role,
        status=user.status,
        exp=user.exp,
        created_at=_format_dt(user.created_at),
    )


def generate_registration_keys(
    db: Session,
    admin_id: int,
    count: int,
    expire_days: int | None = None,
) -> list[RegistrationKeyOut]:
    expires_at = None
    if expire_days:
        expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=expire_days)
    keys = []
    for _ in range(count):
        key = RegistrationKey(code=_gen_key("YUYUE"), created_by=admin_id, expires_at=expires_at)
        db.add(key)
        db.flush()
        keys.append(_registration_key_out(key))
    db.commit()
    return keys


def _registration_key_out(key: RegistrationKey) -> RegistrationKeyOut:
    status = key.status
    now = datetime.now(UTC).replace(tzinfo=None)
    if status == KeyStatus.UNUSED.value and key.expires_at and key.expires_at < now:
        status = KeyStatus.EXPIRED.value
    return RegistrationKeyOut(
        id=key.id,
        code=key.code,
        status=status,
        used_by=key.used_by,
        created_at=_format_dt(key.created_at),
        expires_at=_format_dt(key.expires_at) if key.expires_at else None,
    )


def list_registration_keys(db: Session, params: PageParams) -> PageResult[RegistrationKeyOut]:
    query = db.query(RegistrationKey).order_by(RegistrationKey.created_at.desc())
    total = query.count()
    rows = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    items = [_registration_key_out(k) for k in rows]
    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)


def generate_recovery_key(db: Session, admin_id: int, user_id: int) -> RecoveryKeyOut:
    user = db.get(User, user_id)
    if not user:
        raise_app(ErrorCode.NOT_FOUND, "用户不存在")
    now = datetime.now(UTC).replace(tzinfo=None)
    db.query(RecoveryKey).filter(
        RecoveryKey.user_id == user_id,
        RecoveryKey.status == KeyStatus.UNUSED.value,
    ).update({RecoveryKey.status: KeyStatus.EXPIRED.value}, synchronize_session=False)
    key = RecoveryKey(
        code=_gen_key("RCV"),
        user_id=user_id,
        created_by=admin_id,
        expires_at=now + timedelta(days=7),
    )
    db.add(key)
    db.commit()
    return RecoveryKeyOut(code=key.code, user_id=user.id, nickname=user.nickname)


def _validate_admin_comment_type(comment_type: str) -> None:
    valid = {CommentType.BOOK.value, CommentType.CHAPTER.value, CommentType.PARAGRAPH.value}
    if comment_type not in valid:
        raise_app(ErrorCode.BAD_REQUEST, "无效评论类型")


def list_admin_books(db: Session, params: PageParams) -> PageResult[AdminBookOut]:
    query = db.query(Book).join(User, Book.author_id == User.id).order_by(Book.updated_at.desc())
    total = query.count()
    books = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    items = []
    for b in books:
        author = db.get(User, b.author_id)
        items.append(
            AdminBookOut(
                id=b.id,
                title=b.title,
                author=author.nickname if author else "",
                category=b.category,
                status=b.status,
                admin_delisted=bool(b.admin_delisted),
                word_count=b.word_count,
                updated_at=b.updated_at.strftime("%Y-%m-%d") if b.updated_at else "",
            ),
        )
    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)


def update_admin_book_status(db: Session, book_id: int, status: str) -> AdminBookOut:
    book = db.get(Book, book_id)
    if not book:
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    if status == BookStatus.PUBLISHED.value:
        chapter_count = db.query(Chapter).filter(Chapter.book_id == book_id).count()
        if chapter_count < 1:
            raise_app(ErrorCode.BAD_REQUEST, "至少发布一章才能上架")
    book.status = status
    if status == BookStatus.UNPUBLISHED.value:
        book.admin_delisted = True
    elif status == BookStatus.PUBLISHED.value:
        book.admin_delisted = False
    db.commit()
    db.refresh(book)
    author = db.get(User, book.author_id)
    return AdminBookOut(
        id=book.id,
        title=book.title,
        author=author.nickname if author else "",
        category=book.category,
        status=book.status,
        admin_delisted=bool(book.admin_delisted),
        word_count=book.word_count,
        updated_at=book.updated_at.strftime("%Y-%m-%d") if book.updated_at else "",
    )


def delete_admin_book(db: Session, book_id: int) -> None:
    book = db.get(Book, book_id)
    if not book:
        raise_app(ErrorCode.BOOK_NOT_FOUND)

    chapter_ids = [
        row[0]
        for row in db.query(Chapter.id).filter(Chapter.book_id == book_id).all()
    ]
    if chapter_ids:
        db.query(ParagraphComment).filter(ParagraphComment.chapter_id.in_(chapter_ids)).delete(
            synchronize_session=False,
        )
        db.query(ChapterComment).filter(ChapterComment.chapter_id.in_(chapter_ids)).delete(
            synchronize_session=False,
        )
    db.query(BookComment).filter(BookComment.book_id == book_id).delete(synchronize_session=False)
    db.query(UpdateLog).filter(UpdateLog.book_id == book_id).delete(synchronize_session=False)
    db.query(ReadingProgress).filter(ReadingProgress.book_id == book_id).delete(
        synchronize_session=False,
    )
    db.query(ReadingHistory).filter(ReadingHistory.book_id == book_id).delete(synchronize_session=False)
    db.query(Bookshelf).filter(Bookshelf.book_id == book_id).delete(synchronize_session=False)
    db.query(Chapter).filter(Chapter.book_id == book_id).delete(synchronize_session=False)
    db.delete(book)
    db.commit()


def list_applications(
    db: Session,
    params: PageParams,
    status: str | None = None,
) -> PageResult[AuthorApplicationAdminOut]:
    query = db.query(AuthorApplication).order_by(AuthorApplication.created_at.desc())
    if status and status not in ("", "all"):
        query = query.filter(AuthorApplication.status == status)
    total = query.count()
    rows = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
    items = []
    for app in rows:
        user = db.get(User, app.user_id)
        items.append(
            AuthorApplicationAdminOut(
                id=app.id,
                user_id=app.user_id,
                nickname=user.nickname if user else "",
                reason=app.reason,
                status=app.status,
                created_at=_format_dt(app.created_at),
                review_note=app.review_note,
            ),
        )
    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)


def review_application(
    db: Session,
    app_id: int,
    admin_id: int,
    status: str,
    review_note: str | None,
) -> AuthorApplicationAdminOut:
    app = db.get(AuthorApplication, app_id)
    if not app:
        raise_app(ErrorCode.NOT_FOUND, "申请不存在")

    now = datetime.now(UTC).replace(tzinfo=None)
    result = db.execute(
        update(AuthorApplication)
        .where(
            AuthorApplication.id == app_id,
            AuthorApplication.status == ApplicationStatus.PENDING.value,
        )
        .values(
            status=status,
            review_note=review_note,
            reviewed_by=admin_id,
            reviewed_at=now,
        ),
    )
    if result.rowcount != 1:
        db.rollback()
        raise_app(ErrorCode.CONFLICT, "该申请已处理")

    user = db.get(User, app.user_id)
    if status == ApplicationStatus.APPROVED.value and user and user.role == UserRole.USER.value:
        user.role = UserRole.AUTHOR.value

    db.commit()
    db.refresh(app)
    return AuthorApplicationAdminOut(
        id=app.id,
        user_id=app.user_id,
        nickname=user.nickname if user else "",
        reason=app.reason,
        status=app.status,
        created_at=_format_dt(app.created_at),
        review_note=app.review_note,
    )


def list_admin_comments(
    db: Session,
    comment_type: str,
    page: int,
    page_size: int = 20,
    keyword: str | None = None,
    visibility: str = "visible",
) -> PageResult[AdminCommentOut]:
    _validate_admin_comment_type(comment_type)
    params = PageParams(page=max(1, page), page_size=min(max(1, page_size), 50))
    kw = keyword.strip() if keyword else ""
    like = f"%{kw}%" if kw else None
    show_hidden = visibility == "hidden"
    show_all = visibility == "all"

    if comment_type == "book":
        query = (
            db.query(BookComment, User, Book)
            .join(User, BookComment.user_id == User.id)
            .join(Book, BookComment.book_id == Book.id)
        )
        if not show_all:
            query = query.filter(BookComment.is_hidden.is_(show_hidden))
        if like:
            query = query.filter(
                or_(
                    BookComment.content.ilike(like),
                    User.nickname.ilike(like),
                    Book.title.ilike(like),
                ),
            )
        query = query.order_by(BookComment.created_at.desc())
        total = query.count()
        rows = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
        items = [
            AdminCommentOut(
                id=c.id,
                type="book",
                user=u.nickname,
                user_id=u.id,
                avatar=resolve_avatar(u),
                content=c.content,
                book_title=b.title,
                book_id=b.id,
                is_hidden=c.is_hidden,
                created_at=_format_dt(c.created_at),
            )
            for c, u, b in rows
        ]
    elif comment_type == "paragraph":
        query = (
            db.query(ParagraphComment, User, Chapter, Book)
            .join(User, ParagraphComment.user_id == User.id)
            .join(Chapter, ParagraphComment.chapter_id == Chapter.id)
            .join(Book, Chapter.book_id == Book.id)
        )
        if not show_all:
            query = query.filter(ParagraphComment.is_hidden.is_(show_hidden))
        if like:
            query = query.filter(
                or_(
                    ParagraphComment.content.ilike(like),
                    User.nickname.ilike(like),
                    Book.title.ilike(like),
                    Chapter.title.ilike(like),
                ),
            )
        query = query.order_by(ParagraphComment.created_at.desc())
        total = query.count()
        rows = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
        items = [
            AdminCommentOut(
                id=c.id,
                type="paragraph",
                user=u.nickname,
                user_id=u.id,
                avatar=resolve_avatar(u),
                content=c.content,
                book_title=b.title,
                book_id=b.id,
                chapter_title=ch.title,
                paragraph_index=c.paragraph_index,
                is_hidden=c.is_hidden,
                created_at=_format_dt(c.created_at),
            )
            for c, u, ch, b in rows
        ]
    elif comment_type == "chapter":
        query = (
            db.query(ChapterComment, User, Chapter, Book)
            .join(User, ChapterComment.user_id == User.id)
            .join(Chapter, ChapterComment.chapter_id == Chapter.id)
            .join(Book, Chapter.book_id == Book.id)
        )
        if not show_all:
            query = query.filter(ChapterComment.is_hidden.is_(show_hidden))
        if like:
            query = query.filter(
                or_(
                    ChapterComment.content.ilike(like),
                    User.nickname.ilike(like),
                    Book.title.ilike(like),
                    Chapter.title.ilike(like),
                ),
            )
        query = query.order_by(ChapterComment.created_at.desc())
        total = query.count()
        rows = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()
        items = [
            AdminCommentOut(
                id=c.id,
                type="chapter",
                user=u.nickname,
                user_id=u.id,
                avatar=resolve_avatar(u),
                content=c.content,
                book_title=b.title,
                book_id=b.id,
                chapter_title=ch.title,
                is_hidden=c.is_hidden,
                created_at=_format_dt(c.created_at),
            )
            for c, u, ch, b in rows
        ]
    else:
        raise_app(ErrorCode.BAD_REQUEST, "无效评论类型")

    return PageResult(items=items, total=total, page=params.page, page_size=params.page_size)


def hide_admin_comment(db: Session, comment_id: int, comment_type: str) -> None:
    comment_service.hide_comment(db, comment_id, comment_type)


def unhide_admin_comment(db: Session, comment_id: int, comment_type: str) -> None:
    comment_service.unhide_comment(db, comment_id, comment_type)


def _count_words(content: str) -> int:
    return len(content.replace("\n", "").replace(" ", ""))


def _recalc_book_word_count(db: Session, book: Book) -> None:
    from sqlalchemy import func

    total = (
        db.query(func.coalesce(func.sum(Chapter.word_count), 0))
        .filter(Chapter.book_id == book.id)
        .scalar()
    )
    book.word_count = int(total or 0)


def list_admin_chapters(db: Session, book_id: int) -> list[AdminChapterOut]:
    book = db.get(Book, book_id)
    if not book:
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    chapters = (
        db.query(Chapter)
        .filter(Chapter.book_id == book_id)
        .order_by(Chapter.sort_order, Chapter.id)
        .all()
    )
    return [
        AdminChapterOut(
            id=c.id,
            title=c.title,
            word_count=c.word_count,
            sort_order=c.sort_order,
            updated_at=_format_dt(c.updated_at),
        )
        for c in chapters
    ]


def get_admin_chapter(db: Session, chapter_id: int) -> AdminChapterDetailOut:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise_app(ErrorCode.CHAPTER_NOT_FOUND)
    book = db.get(Book, chapter.book_id)
    if not book:
        raise_app(ErrorCode.BOOK_NOT_FOUND)
    return AdminChapterDetailOut(
        id=chapter.id,
        book_id=chapter.book_id,
        book_title=book.title,
        title=chapter.title,
        content=chapter.content,
        word_count=chapter.word_count,
        sort_order=chapter.sort_order,
        updated_at=_format_dt(chapter.updated_at),
    )


def update_admin_chapter(
    db: Session,
    chapter_id: int,
    data: AdminUpdateChapterRequest,
) -> AdminChapterDetailOut:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise_app(ErrorCode.CHAPTER_NOT_FOUND)
    book = db.get(Book, chapter.book_id)
    if data.title is not None:
        chapter.title = data.title
    if data.content is not None:
        validate_chapter_content(data.content)
        chapter.content = normalize_chapter_content(data.content)
        chapter.word_count = _count_words(chapter.content)
    db.flush()
    if book:
        _recalc_book_word_count(db, book)
    db.commit()
    db.refresh(chapter)
    return get_admin_chapter(db, chapter_id)
