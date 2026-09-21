"""API v1 路由聚合。"""

from fastapi import APIRouter

from app.api.v1 import auth, author, books, bookshelf, chapters, comments, profile, reading, upload, users
from app.api.v1.admin import admin_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(books.router)
api_v1_router.include_router(chapters.router)
api_v1_router.include_router(comments.router)
api_v1_router.include_router(bookshelf.router)
api_v1_router.include_router(reading.router)
api_v1_router.include_router(profile.router)
api_v1_router.include_router(author.router)
api_v1_router.include_router(upload.router)
api_v1_router.include_router(admin_router)
