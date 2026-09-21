"""统一 API 响应与分页模型 — 数据流出口格式（后端）。"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """所有接口的统一响应包装。禁止裸返回 dict。"""

    code: int = 0
    message: str = "ok"
    data: T | None = None


class PageParams(BaseModel):
    page: int = Field(default=DEFAULT_PAGE, ge=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


def ok(data: T | None = None, message: str = "ok") -> ApiResponse[T]:
    return ApiResponse(code=0, message=message, data=data)


def fail(code: int, message: str) -> ApiResponse[None]:
    return ApiResponse(code=code, message=message, data=None)
