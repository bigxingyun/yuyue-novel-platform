"""找回密钥、书籍上下架、评论隐藏恢复测试。"""

import uuid

import pytest

from app.core.constants import BookStatus, KeyStatus
from app.core.exceptions import AppException
from app.core.security import hash_password
from app.database import SessionLocal
from app.models import Book, Chapter, ChapterComment, RecoveryKey, User
from app.services import admin_service, auth_service, comment_service
from app.services.author_service import publish_book, unpublish_book


def _unique(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _create_user(db, role: str = "user") -> User:
    user = User(nickname=_unique("u"), password_hash=hash_password("test123"), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_recover_password_with_valid_key():
    db = SessionLocal()
    admin = _create_user(db, "admin")
    reader = _create_user(db)
    try:
        result = admin_service.generate_recovery_key(db, admin.id, reader.id)
        auth_service.recover_password(
            db,
            account=reader.nickname,
            recovery_key=result.code,
            new_password="newpass123",
        )
        key = db.query(RecoveryKey).filter(RecoveryKey.code == result.code).first()
        assert key is not None
        assert key.status == KeyStatus.USED.value
        tokens = auth_service.login(db, reader.nickname, "newpass123")
        assert tokens.user.nickname == reader.nickname
    finally:
        db.query(RecoveryKey).filter(RecoveryKey.user_id == reader.id).delete()
        db.delete(reader)
        db.delete(admin)
        db.commit()
        db.close()


def test_admin_republish_blocks_author_until_admin_approves():
    db = SessionLocal()
    author = _create_user(db, "author")
    admin = _create_user(db, "admin")
    book = Book(title="测试书", author_id=author.id, status=BookStatus.PUBLISHED.value)
    db.add(book)
    db.commit()
    db.refresh(book)
    chapter = Chapter(book_id=book.id, title="第一章", content="正文", word_count=2, sort_order=1)
    db.add(chapter)
    db.commit()
    try:
        admin_service.update_admin_book_status(db, book.id, BookStatus.UNPUBLISHED.value)
        db.refresh(book)
        assert book.admin_delisted is True

        with pytest.raises(AppException):
            unpublish_book(db, author.id, book.id)

        with pytest.raises(AppException):
            publish_book(db, author.id, book.id)

        admin_service.update_admin_book_status(db, book.id, BookStatus.PUBLISHED.value)
        db.refresh(book)
        assert book.status == BookStatus.PUBLISHED.value
        assert book.admin_delisted is False
        published = publish_book(db, author.id, book.id)
        assert published.status == BookStatus.PUBLISHED.value
    finally:
        db.delete(chapter)
        db.delete(book)
        db.delete(author)
        db.delete(admin)
        db.commit()
        db.close()


def test_unhide_comment():
    db = SessionLocal()
    author = _create_user(db, "author")
    reader = _create_user(db)
    book = Book(title="评论书", author_id=author.id, status=BookStatus.PUBLISHED.value)
    db.add(book)
    db.commit()
    db.refresh(book)
    chapter = Chapter(book_id=book.id, title="第一章", content="正文", word_count=2, sort_order=1)
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    comment = ChapterComment(chapter_id=chapter.id, user_id=reader.id, content="待隐藏评论")
    db.add(comment)
    db.commit()
    db.refresh(comment)
    try:
        comment_service.hide_comment(db, comment.id, "chapter")
        db.refresh(comment)
        assert comment.is_hidden is True

        comment_service.unhide_comment(db, comment.id, "chapter")
        db.refresh(comment)
        assert comment.is_hidden is False
    finally:
        db.delete(comment)
        db.delete(chapter)
        db.delete(book)
        db.delete(reader)
        db.delete(author)
        db.commit()
        db.close()
