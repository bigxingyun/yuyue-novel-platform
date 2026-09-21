"""评论业务逻辑。"""



from sqlalchemy.orm import Session



from app.core.constants import ErrorCode, UserRole

from app.core.exceptions import raise_app

from app.models import Book, BookComment, Chapter, ChapterComment, ParagraphComment, User

from app.schemas.comment import CommentOut

from app.services.exp_service import award_comment_exp
from app.services.title_service import get_title_info
from app.utils.avatar import resolve_avatar
from app.utils.book_access import require_published_book, require_published_chapter


def _user_comment_fields(db: Session, user_id: int) -> dict:
    user = db.get(User, user_id)
    info = get_title_info(user.exp if user else 0)
    return {
        "avatar": resolve_avatar(user),
        "level": info.level,
        "title": info.title,
    }


def _para_out(db: Session, comment: ParagraphComment) -> CommentOut:

    user = db.get(User, comment.user_id)
    extra = _user_comment_fields(db, comment.user_id)

    return CommentOut(

        id=comment.id,

        user=user.nickname if user else "读者",

        user_id=comment.user_id,

        content=comment.content,

        is_pinned=comment.is_pinned,

        parent_id=comment.parent_id,

        **extra,

    )





def _chapter_out(db: Session, comment: ChapterComment) -> CommentOut:

    user = db.get(User, comment.user_id)
    extra = _user_comment_fields(db, comment.user_id)

    return CommentOut(

        id=comment.id,

        user=user.nickname if user else "读者",

        user_id=comment.user_id,

        content=comment.content,

        is_pinned=comment.is_pinned,

        parent_id=comment.parent_id,

        **extra,

    )





def _book_out(db: Session, comment: BookComment) -> CommentOut:

    user = db.get(User, comment.user_id)
    extra = _user_comment_fields(db, comment.user_id)

    return CommentOut(

        id=comment.id,

        user=user.nickname if user else "读者",

        user_id=comment.user_id,

        content=comment.content,

        is_pinned=comment.is_pinned,

        parent_id=comment.parent_id,

        **extra,

    )





def _build_tree(comments: list, out_fn) -> list[CommentOut]:

    items = {c.id: out_fn(c) for c in comments}

    roots: list[CommentOut] = []

    for c in comments:

        node = items[c.id]

        if c.parent_id and c.parent_id in items:

            items[c.parent_id].replies.append(node)

        elif not c.parent_id:

            roots.append(node)

    return roots





def _validate_parent(db: Session, model, parent_id: int | None, scope_filter) -> None:

    if not parent_id:

        return

    parent = db.get(model, parent_id)

    if not parent or not scope_filter(parent):

        raise_app(ErrorCode.NOT_FOUND, "回复目标不存在")

    if parent.parent_id:

        raise_app(ErrorCode.BAD_REQUEST, "仅支持一级回复")





def list_paragraph_comments(

    db: Session,

    chapter_id: int,

    paragraph_index: int,

) -> list[CommentOut]:

    require_published_chapter(db, chapter_id)



    comments = (

        db.query(ParagraphComment)

        .filter(

            ParagraphComment.chapter_id == chapter_id,

            ParagraphComment.paragraph_index == paragraph_index,

            ParagraphComment.is_hidden.is_(False),

        )

        .order_by(ParagraphComment.is_pinned.desc(), ParagraphComment.created_at.asc())

        .all()

    )

    return _build_tree(comments, lambda c: _para_out(db, c))





def create_paragraph_comment(

    db: Session,

    chapter_id: int,

    paragraph_index: int,

    user_id: int,

    content: str,

    parent_id: int | None = None,

) -> CommentOut:

    require_published_chapter(db, chapter_id)

    _validate_parent(

        db,

        ParagraphComment,

        parent_id,

        lambda p: p.chapter_id == chapter_id and p.paragraph_index == paragraph_index,

    )

    comment = ParagraphComment(

        chapter_id=chapter_id,

        paragraph_index=paragraph_index,

        user_id=user_id,

        content=content,

        parent_id=parent_id,

    )

    db.add(comment)

    award_comment_exp(db, user_id)

    db.commit()

    db.refresh(comment)

    return _para_out(db, comment)





def list_chapter_comments(db: Session, chapter_id: int) -> list[CommentOut]:

    require_published_chapter(db, chapter_id)



    comments = (

        db.query(ChapterComment)

        .filter(ChapterComment.chapter_id == chapter_id, ChapterComment.is_hidden.is_(False))

        .order_by(ChapterComment.is_pinned.desc(), ChapterComment.created_at.asc())

        .all()

    )

    return _build_tree(comments, lambda c: _chapter_out(db, c))





def create_chapter_comment(

    db: Session,

    chapter_id: int,

    user_id: int,

    content: str,

    parent_id: int | None = None,

) -> CommentOut:

    require_published_chapter(db, chapter_id)

    _validate_parent(

        db,

        ChapterComment,

        parent_id,

        lambda p: p.chapter_id == chapter_id,

    )

    comment = ChapterComment(

        chapter_id=chapter_id,

        user_id=user_id,

        content=content,

        parent_id=parent_id,

    )

    db.add(comment)

    award_comment_exp(db, user_id)

    db.commit()

    db.refresh(comment)

    return _chapter_out(db, comment)





def list_paragraph_comments_by_chapter(db: Session, chapter_id: int) -> dict[int, list[CommentOut]]:

    require_published_chapter(db, chapter_id)



    comments = (

        db.query(ParagraphComment)

        .filter(ParagraphComment.chapter_id == chapter_id, ParagraphComment.is_hidden.is_(False))

        .order_by(

            ParagraphComment.paragraph_index,

            ParagraphComment.is_pinned.desc(),

            ParagraphComment.created_at.asc(),

        )

        .all()

    )

    grouped: dict[int, list[ParagraphComment]] = {}

    for c in comments:

        grouped.setdefault(c.paragraph_index, []).append(c)

    return {

        idx: _build_tree(rows, lambda c: _para_out(db, c))

        for idx, rows in grouped.items()

    }





def list_book_comments(db: Session, book_id: int) -> list[CommentOut]:

    require_published_book(db, book_id)



    comments = (

        db.query(BookComment)

        .filter(BookComment.book_id == book_id, BookComment.is_hidden.is_(False))

        .order_by(BookComment.is_pinned.desc(), BookComment.created_at.asc())

        .all()

    )

    return _build_tree(comments, lambda c: _book_out(db, c))





def create_book_comment(

    db: Session,

    book_id: int,

    user_id: int,

    content: str,

    parent_id: int | None = None,

) -> CommentOut:

    require_published_book(db, book_id)

    _validate_parent(

        db,

        BookComment,

        parent_id,

        lambda p: p.book_id == book_id,

    )

    comment = BookComment(book_id=book_id, user_id=user_id, content=content, parent_id=parent_id)

    db.add(comment)

    award_comment_exp(db, user_id)

    db.commit()

    db.refresh(comment)

    return _book_out(db, comment)





def _get_book_author_id(db: Session, book_id: int) -> int | None:

    book = db.get(Book, book_id)

    return book.author_id if book else None





def _can_manage_comment(db: Session, user: User, book_id: int, comment_user_id: int) -> bool:

    if user.id == comment_user_id:

        return True

    if user.role in (UserRole.ADMIN.value, UserRole.SUPERADMIN.value):

        return True

    author_id = _get_book_author_id(db, book_id)

    return author_id == user.id





def delete_comment(db: Session, user: User, comment_id: int, comment_type: str) -> None:

    if comment_type == "paragraph":

        comment = db.get(ParagraphComment, comment_id)

        if not comment:

            raise_app(ErrorCode.NOT_FOUND, "评论不存在")

        chapter = db.get(Chapter, comment.chapter_id)

        if not chapter or not _can_manage_comment(db, user, chapter.book_id, comment.user_id):

            raise_app(ErrorCode.FORBIDDEN)

        db.query(ParagraphComment).filter(ParagraphComment.parent_id == comment.id).delete()

        db.delete(comment)

    elif comment_type == "chapter":

        comment = db.get(ChapterComment, comment_id)

        if not comment:

            raise_app(ErrorCode.NOT_FOUND, "评论不存在")

        chapter = db.get(Chapter, comment.chapter_id)

        if not chapter or not _can_manage_comment(db, user, chapter.book_id, comment.user_id):

            raise_app(ErrorCode.FORBIDDEN)

        db.query(ChapterComment).filter(ChapterComment.parent_id == comment.id).delete()

        db.delete(comment)

    elif comment_type == "book":

        comment = db.get(BookComment, comment_id)

        if not comment:

            raise_app(ErrorCode.NOT_FOUND, "评论不存在")

        if not _can_manage_comment(db, user, comment.book_id, comment.user_id):

            raise_app(ErrorCode.FORBIDDEN)

        db.query(BookComment).filter(BookComment.parent_id == comment.id).delete()

        db.delete(comment)

    else:

        raise_app(ErrorCode.BAD_REQUEST, "无效评论类型")

    db.commit()





def pin_comment(db: Session, user: User, comment_id: int, comment_type: str) -> CommentOut:

    if comment_type == "paragraph":

        comment = db.get(ParagraphComment, comment_id)

        if not comment:

            raise_app(ErrorCode.NOT_FOUND, "评论不存在")

        chapter = db.get(Chapter, comment.chapter_id)

        if not chapter:

            raise_app(ErrorCode.CHAPTER_NOT_FOUND)

        author_id = _get_book_author_id(db, chapter.book_id)

        if user.id != author_id and user.role not in (UserRole.ADMIN.value, UserRole.SUPERADMIN.value):

            raise_app(ErrorCode.FORBIDDEN)

        db.query(ParagraphComment).filter(

            ParagraphComment.chapter_id == comment.chapter_id,

            ParagraphComment.paragraph_index == comment.paragraph_index,

        ).update({ParagraphComment.is_pinned: False})

        comment.is_pinned = True

        db.commit()

        db.refresh(comment)

        return _para_out(db, comment)



    if comment_type == "chapter":

        comment = db.get(ChapterComment, comment_id)

        if not comment:

            raise_app(ErrorCode.NOT_FOUND, "评论不存在")

        chapter = db.get(Chapter, comment.chapter_id)

        if not chapter:

            raise_app(ErrorCode.CHAPTER_NOT_FOUND)

        author_id = _get_book_author_id(db, chapter.book_id)

        if user.id != author_id and user.role not in (UserRole.ADMIN.value, UserRole.SUPERADMIN.value):

            raise_app(ErrorCode.FORBIDDEN)

        db.query(ChapterComment).filter(ChapterComment.chapter_id == comment.chapter_id).update(

            {ChapterComment.is_pinned: False},

        )

        comment.is_pinned = True

        db.commit()

        db.refresh(comment)

        return _chapter_out(db, comment)



    if comment_type == "book":

        comment = db.get(BookComment, comment_id)

        if not comment:

            raise_app(ErrorCode.NOT_FOUND, "评论不存在")

        author_id = _get_book_author_id(db, comment.book_id)

        if user.id != author_id and user.role not in (UserRole.ADMIN.value, UserRole.SUPERADMIN.value):

            raise_app(ErrorCode.FORBIDDEN)

        db.query(BookComment).filter(BookComment.book_id == comment.book_id).update(

            {BookComment.is_pinned: False},

        )

        comment.is_pinned = True

        db.commit()

        db.refresh(comment)

        return _book_out(db, comment)



    raise_app(ErrorCode.BAD_REQUEST, "无效评论类型")





def hide_comment(db: Session, comment_id: int, comment_type: str) -> None:

    model_map = {

        "paragraph": ParagraphComment,

        "chapter": ChapterComment,

        "book": BookComment,

    }

    model = model_map.get(comment_type)

    if not model:

        raise_app(ErrorCode.BAD_REQUEST, "无效评论类型")

    comment = db.get(model, comment_id)

    if not comment:

        raise_app(ErrorCode.NOT_FOUND, "评论不存在")

    comment.is_hidden = True

    db.commit()


def unhide_comment(db: Session, comment_id: int, comment_type: str) -> None:
    model_map = {
        "paragraph": ParagraphComment,
        "chapter": ChapterComment,
        "book": BookComment,
    }

    model = model_map.get(comment_type)

    if not model:
        raise_app(ErrorCode.BAD_REQUEST, "无效评论类型")

    comment = db.get(model, comment_id)

    if not comment:
        raise_app(ErrorCode.NOT_FOUND, "评论不存在")

    comment.is_hidden = False

    db.commit()


