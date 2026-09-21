"""配置解析回归测试。

背景：`cors_origins` 是 `list[str]`，pydantic-settings 默认按 JSON 解析该字段，
环境变量写成裸 URL 时会在导入期抛 SettingsError。CI 与照抄 .env.example 的用户
都踩过这个坑，这里锁定三种写法都能正常解析。
"""

from app.config import Settings, parse_cors_origins


def test_parse_bare_url():
    assert parse_cors_origins("http://localhost:5173") == ["http://localhost:5173"]


def test_parse_json_array():
    assert parse_cors_origins('["http://a.test", "https://b.test"]') == [
        "http://a.test",
        "https://b.test",
    ]


def test_parse_comma_separated():
    assert parse_cors_origins("http://a.test, https://b.test") == [
        "http://a.test",
        "https://b.test",
    ]


def test_parse_empty():
    assert parse_cors_origins("") == []
    assert parse_cors_origins(None) == []


def test_settings_accepts_bare_url_from_env(monkeypatch):
    """裸 URL 也必须能构建 Settings —— 这是 CI 之前失败的根因。"""
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    assert Settings().cors_origins == ["http://localhost:5173"]


def test_settings_accepts_json_array_from_env(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", '["http://a.test","http://b.test"]')
    assert Settings().cors_origins == ["http://a.test", "http://b.test"]
