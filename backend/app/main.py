"""FastAPI 应用入口。"""

import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_v1_router
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.seed import init_db


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """登录/注册等接口简易限流（每 IP 每分钟 30 次）。"""

    def __init__(self, app, limit: int = 30, window_sec: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_sec = window_sec
        self.hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/v1/auth/"):
            return await call_next(request)
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = self.hits[ip]
        self.hits[ip] = [t for t in window if now - t < self.window_sec]
        if len(self.hits[ip]) >= self.limit:
            return JSONResponse(status_code=429, content={"code": 429, "message": "请求过于频繁"})
        self.hits[ip].append(now)
        return await call_next(request)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


_is_prod = settings.environment == "production"

app = FastAPI(
    title="欲阅 API",
    version="0.1.0",
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.add_middleware(AuthRateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_v1_router, prefix="/api/v1")

upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")


def mount_frontend(app: FastAPI) -> None:
    """生产单端口模式：由后端同时托管前端 dist（无需 Nginx）。"""
    if not settings.frontend_dist:
        return

    dist = Path(settings.frontend_dist).resolve()
    if not dist.is_dir():
        return

    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="frontend-assets")

    @app.get("/{spa_path:path}", include_in_schema=False)
    async def spa_fallback(spa_path: str):
        if spa_path.startswith(("api/", "uploads/")):
            raise HTTPException(status_code=404)
        if spa_path:
            candidate = (dist / spa_path).resolve()
            if not str(candidate).startswith(str(dist)):
                raise HTTPException(status_code=404)
            if candidate.is_file():
                return FileResponse(candidate)
        index = dist / "index.html"
        if not index.is_file():
            raise HTTPException(status_code=404, detail="frontend dist missing index.html")
        return FileResponse(index)


mount_frontend(app)
