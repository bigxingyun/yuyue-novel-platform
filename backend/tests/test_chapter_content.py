"""章节正文解析测试。"""

import pytest

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.utils.chapter_content import (
    normalize_chapter_content,
    normalize_image_url,
    parse_chapter_blocks,
    validate_chapter_content,
)


def test_parse_text_and_image_blocks():
    content = "第一段。\n\n第二段。\n\n[img:/uploads/abc.png]\n\n第三段。"
    blocks = parse_chapter_blocks(content)
    assert len(blocks) == 4
    assert blocks[0]["type"] == "text"
    assert blocks[0]["paragraph_index"] == 0
    assert blocks[2]["type"] == "image"
    assert blocks[2]["after_paragraph_index"] == 1
    assert blocks[2]["url"] == "/uploads/abc.png"


def test_normalize_legacy_localhost_upload_url():
    assert normalize_image_url("http://127.0.0.1:5173/uploads/a.png") == "/uploads/a.png"
    assert normalize_image_url("https://localhost:5173/uploads/b.jpg") == "/uploads/b.jpg"


def test_parse_content_with_legacy_http_marker():
    content = "段落。\n\n[img:http://localhost:5173/uploads/x.png]"
    blocks = parse_chapter_blocks(content)
    assert len(blocks) == 2
    assert blocks[1]["type"] == "image"
    assert blocks[1]["url"] == "/uploads/x.png"


def test_reject_external_url_in_marker():
    with pytest.raises(AppException) as exc:
        validate_chapter_content("[img:https://evil.example/x?/uploads/abc.png]")
    assert exc.value.code == ErrorCode.BAD_REQUEST


def test_normalize_valid_marker():
    content = "段落。\n\n[img:/uploads/test.jpg]"
    normalized = normalize_chapter_content(content)
    assert "[img:/uploads/test.jpg]" in normalized
    validate_chapter_content(normalized)
