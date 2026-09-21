"""评论路由。"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.comment import CreateChapterCommentRequest, CreateParagraphCommentRequest
from app.schemas.common import ok
from app.services import comment_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/paragraph/by-chapter/{chapter_id}")
def list_paragraph_comments_by_chapter(chapter_id: int, db: DbSession):
    return ok(comment_service.list_paragraph_comments_by_chapter(db, chapter_id))


@router.get("/paragraph")
def list_paragraph_comments(
    db: DbSession,
    chapter_id: int,
    paragraph_index: int,
):
    return ok(comment_service.list_paragraph_comments(db, chapter_id, paragraph_index))


@router.post("/paragraph")
def create_paragraph_comment(
    body: CreateParagraphCommentRequest,
    db: DbSession,
    user: CurrentUser,
):
    return ok(
        comment_service.create_paragraph_comment(
            db,
            body.chapter_id,
            body.paragraph_index,
            user.id,
            body.content,
            body.parent_id,
        ),
    )


@router.get("/chapter/{chapter_id}")
def list_chapter_comments(chapter_id: int, db: DbSession):
    return ok(comment_service.list_chapter_comments(db, chapter_id))


@router.post("/chapter")
def create_chapter_comment(
    body: CreateChapterCommentRequest,
    db: DbSession,
    user: CurrentUser,
):
    return ok(
        comment_service.create_chapter_comment(
            db, body.chapter_id, user.id, body.content, body.parent_id,
        ),
    )


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: DbSession,
    user: CurrentUser,
    type: str,
):
    comment_service.delete_comment(db, user, comment_id, type)
    return ok(None, message="已删除")


@router.post("/{comment_id}/pin")
def pin_comment(
    comment_id: int,
    db: DbSession,
    user: CurrentUser,
    type: str,
):
    return ok(comment_service.pin_comment(db, user, comment_id, type))
