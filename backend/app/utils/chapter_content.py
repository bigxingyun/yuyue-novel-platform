"""章节正文解析：文本段与图片块。"""

import re
from urllib.parse import urlparse

IMG_MARKER_PATTERN = re.compile(r"^\[img:(.+)\]$")
_UPLOADS_PATH = re.compile(r"(/uploads/[^\]\s]+)")


def normalize_image_url(url: str) -> str:
    """将图片地址规范为 /uploads/... 相对路径；拒绝真外链。"""
    trimmed = url.strip()
    if trimmed.startswith("/uploads/"):
        return trimmed
    lower = trimmed.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        path = urlparse(trimmed).path
        if path.startswith("/uploads/"):
            return path
        raise ValueError("图片地址不允许使用外链")
    match = _UPLOADS_PATH.search(trimmed)
    if match:
        return match.group(1)
    return trimmed


def parse_chapter_blocks(content: str) -> list[dict]:
    """将章节 content 解析为 text / image 块列表。"""
    blocks: list[dict] = []
    paragraph_index = -1
    for raw in content.split("\n\n"):
        block = raw.strip()
        if not block:
            continue
        match = IMG_MARKER_PATTERN.match(block)
        if match:
            blocks.append(
                {
                    "type": "image",
                    "url": normalize_image_url(match.group(1)),
                    "after_paragraph_index": paragraph_index,
                },
            )
        else:
            paragraph_index += 1
            blocks.append(
                {
                    "type": "text",
                    "text": block,
                    "paragraph_index": paragraph_index,
                },
            )
    return blocks


def split_paragraphs(content: str) -> list[str]:
    """仅返回文本段（兼容旧接口）。"""
    return [b["text"] for b in parse_chapter_blocks(content) if b["type"] == "text"]


def normalize_chapter_content(content: str) -> str:
    """规范化 content 中所有图片 marker 的 URL。"""
    parts: list[str] = []
    for raw in content.split("\n\n"):
        block = raw.strip()
        if not block:
            continue
        match = IMG_MARKER_PATTERN.match(block)
        if match:
            parts.append(f"[img:{normalize_image_url(match.group(1))}]")
        else:
            parts.append(block)
    return "\n\n".join(parts)


def validate_chapter_content(content: str) -> None:
    """校验 content 中图片 marker 的 URL 必须为本站 /uploads/ 路径。"""
    from app.core.constants import ErrorCode
    from app.core.exceptions import raise_app

    try:
        normalized = normalize_chapter_content(content)
    except ValueError:
        raise_app(ErrorCode.BAD_REQUEST, "图片地址无效，仅支持本站上传路径")
    for raw in normalized.split("\n\n"):
        block = raw.strip()
        if not block:
            continue
        match = IMG_MARKER_PATTERN.match(block)
        if match:
            url = match.group(1)
            if not url.startswith("/uploads/"):
                raise_app(ErrorCode.BAD_REQUEST, "图片地址无效，仅支持本站上传路径")
