"""作者端路由。"""



from fastapi import APIRouter



from app.api.deps import AuthorUser, DbSession

from app.schemas.author import (

    CreateBookRequest,

    CreateChapterRequest,

    ReorderChaptersRequest,

    UpdateBookRequest,

    UpdateChapterRequest,

)

from app.schemas.common import ok

from app.services import author_service



router = APIRouter(prefix="/author", tags=["author"])





@router.get("/books")

def list_books(db: DbSession, user: AuthorUser):

    return ok(author_service.list_author_books(db, user.id))





@router.post("/books")

def create_book(body: CreateBookRequest, db: DbSession, user: AuthorUser):

    return ok(author_service.create_book(db, user.id, body))





@router.patch("/books/{book_id}")

def update_book(book_id: int, body: UpdateBookRequest, db: DbSession, user: AuthorUser):

    return ok(author_service.update_book(db, user.id, book_id, body))





@router.post("/books/{book_id}/publish")

def publish_book(book_id: int, db: DbSession, user: AuthorUser):

    return ok(author_service.publish_book(db, user.id, book_id))





@router.post("/books/{book_id}/unpublish")

def unpublish_book(book_id: int, db: DbSession, user: AuthorUser):

    return ok(author_service.unpublish_book(db, user.id, book_id))





@router.delete("/books/{book_id}")

def delete_book(book_id: int, db: DbSession, user: AuthorUser):

    author_service.delete_book(db, user.id, book_id)

    return ok(None, message="已删除")





@router.get("/books/{book_id}/chapters")

def list_chapters(book_id: int, db: DbSession, user: AuthorUser):

    return ok(author_service.list_chapters(db, user.id, book_id))





@router.post("/books/{book_id}/chapters")

def create_chapter(

    book_id: int,

    body: CreateChapterRequest,

    db: DbSession,

    user: AuthorUser,

):

    return ok(author_service.create_chapter(db, user.id, book_id, body))





@router.get("/chapters/{chapter_id}")
def get_chapter(chapter_id: int, db: DbSession, user: AuthorUser):
    return ok(author_service.get_chapter(db, user.id, chapter_id))


@router.patch("/chapters/{chapter_id}")

def update_chapter(

    chapter_id: int,

    body: UpdateChapterRequest,

    db: DbSession,

    user: AuthorUser,

):

    return ok(author_service.update_chapter(db, user.id, chapter_id, body))





@router.delete("/chapters/{chapter_id}")

def delete_chapter(chapter_id: int, db: DbSession, user: AuthorUser):

    author_service.delete_chapter(db, user.id, chapter_id)

    return ok(None, message="已删除")





@router.put("/books/{book_id}/chapters/reorder")

def reorder_chapters(

    book_id: int,

    body: ReorderChaptersRequest,

    db: DbSession,

    user: AuthorUser,

):

    return ok(author_service.reorder_chapters(db, user.id, book_id, body.chapter_ids))


