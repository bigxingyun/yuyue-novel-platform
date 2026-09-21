"""业务异常定义与全局异常处理器。"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.constants import ErrorCode
from app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)

# 默认用户可见文案（message 可覆盖）
DEFAULT_ERROR_MESSAGES: dict[int, str] = {
    ErrorCode.BAD_REQUEST: "请求参数错误",
    ErrorCode.UNAUTHORIZED: "未登录或登录已失效",
    ErrorCode.FORBIDDEN: "无权执行此操作",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.CONFLICT: "操作冲突",
    ErrorCode.INTERNAL_ERROR: "服务器繁忙，请稍后重试",
    ErrorCode.REGISTRATION_KEY_INVALID: "注册码无效或已使用",
    ErrorCode.NICKNAME_TAKEN: "昵称已被占用",
    ErrorCode.TOKEN_EXPIRED: "登录已过期，请重新登录",
    ErrorCode.ACCOUNT_BANNED: "账号已被封禁，请联系管理员",
    ErrorCode.AUTHOR_REQUIRED: "需要作者权限",
    ErrorCode.ADMIN_REQUIRED: "需要管理员权限",
    ErrorCode.BOOK_NOT_FOUND: "书籍不存在",
    ErrorCode.CHAPTER_NOT_FOUND: "章节不存在",
    ErrorCode.ALREADY_CHECKED_IN: "今日已签到",
}


def http_status_for_code(code: int) -> int:
    """业务 code → HTTP 状态码。"""
    if code == ErrorCode.OK:
        return 200
    if code == ErrorCode.UNAUTHORIZED or code == ErrorCode.TOKEN_EXPIRED:
        return 401
    if code in (ErrorCode.FORBIDDEN, ErrorCode.ACCOUNT_BANNED, ErrorCode.AUTHOR_REQUIRED, ErrorCode.ADMIN_REQUIRED):
        return 403
    if code in (ErrorCode.NOT_FOUND, ErrorCode.BOOK_NOT_FOUND, ErrorCode.CHAPTER_NOT_FOUND):
        return 404
    if code in (ErrorCode.CONFLICT, ErrorCode.ALREADY_CHECKED_IN, ErrorCode.NICKNAME_TAKEN):
        return 409
    if code == ErrorCode.INTERNAL_ERROR:
        return 500
    if code >= 40001:
        if 40101 <= code < 40200:
            return 401
        if 40301 <= code < 40400:
            return 403
        if 40401 <= code < 40500:
            return 404
        if 40901 <= code < 41000:
            return 409
        if 40001 <= code < 40100:
            return 400
    if code == ErrorCode.BAD_REQUEST:
        return 400
    return 400


class AppException(Exception):
    """可预期的业务异常 — 仅 Service 层抛出。"""

    def __init__(
        self,
        code: int,
        message: str | None = None,
        *,
        http_status: int | None = None,
        data: Any = None,
    ) -> None:
        self.code = code
        self.message = message or DEFAULT_ERROR_MESSAGES.get(code, "操作失败")
        self.http_status = http_status or http_status_for_code(code)
        self.data = data
        super().__init__(self.message)


def raise_app(code: int, message: str | None = None, **kwargs: Any) -> None:
    """在 Service 中抛出业务异常的简写。"""
    raise AppException(code, message, **kwargs)


def _error_response(code: int, message: str, http_status: int) -> JSONResponse:
    body = ApiResponse(code=code, message=message, data=None)
    return JSONResponse(status_code=http_status, content=body.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器 — 在 main.py 中调用一次。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        return _error_response(exc.code, exc.message, exc.http_status)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        detail = "；".join(
            f"{'.'.join(str(loc) for loc in err['loc'] if loc != 'body')}: {err['msg']}"
            for err in errors[:3]
        )
        message = f"参数校验失败：{detail}" if detail else "参数校验失败"
        return _error_response(ErrorCode.BAD_REQUEST, message, 422)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code_map = {
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.CONFLICT,
        }
        code = code_map.get(exc.status_code, ErrorCode.BAD_REQUEST)
        message = str(exc.detail) if exc.detail else DEFAULT_ERROR_MESSAGES.get(code, "请求失败")
        return _error_response(code, message, exc.status_code)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s %s", request.method, request.url.path, exc_info=exc)
        return _error_response(
            ErrorCode.INTERNAL_ERROR,
            DEFAULT_ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR],
            500,
        )
