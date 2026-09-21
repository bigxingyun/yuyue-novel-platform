"""管理后台路由聚合。"""

from fastapi import APIRouter

from app.api.v1.admin import applications, books, chapters, comments, keys, users

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(users.router)
admin_router.include_router(keys.router)
admin_router.include_router(books.router)
admin_router.include_router(chapters.router)
admin_router.include_router(applications.router)
admin_router.include_router(comments.router)
