"""文件上传。"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.core.constants import ErrorCode
from app.core.exceptions import raise_app

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def _detect_image_mime(data: bytes) -> str | None:
    if len(data) >= 3 and data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if len(data) >= 6 and data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def save_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise_app(ErrorCode.BAD_REQUEST, "仅支持 JPG/PNG/WebP/GIF 图片")

    data = file.file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise_app(ErrorCode.BAD_REQUEST, f"图片不能超过 {settings.max_upload_mb}MB")

    detected = _detect_image_mime(data)
    if not detected or detected not in ALLOWED_TYPES:
        raise_app(ErrorCode.BAD_REQUEST, "文件内容不是有效的图片")

    ext = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }[detected]

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    path = upload_dir / filename
    path.write_bytes(data)
    return f"/uploads/{filename}"
