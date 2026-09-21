"""应用配置。"""

import json
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

try:  # pydantic-settings >= 2.3 提供 NoDecode；更早版本没有，见下方兼容分支
    from pydantic_settings import NoDecode
except ImportError:  # pragma: no cover
    NoDecode = None  # type: ignore[assignment]


def parse_cors_origins(value: object) -> list[str]:
    """解析 CORS 来源，兼容三种写法：

    - JSON 数组：`["http://localhost:5173", "https://a.com"]`
    - 逗号分隔：`http://localhost:5173,https://a.com`
    - 单个裸 URL：`http://localhost:5173`

    说明：pydantic-settings 默认按 JSON 解析 `list[str]` 字段，裸 URL 会直接抛
    SettingsError（CI 与照抄 .env.example 的用户都会踩到），因此这里放宽为
    「JSON 优先，失败则按逗号切分」。新版本配合 NoDecode 关闭前置解码。
    """
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                # 更早的 pydantic-settings 已把值按 JSON 解码过，兜底再切一次逗号
                return [item.strip() for item in text.split(",") if item.strip()]
            return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in text.split(",") if item.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value)]


_CorsOrigins = Annotated[list[str], NoDecode] if NoDecode else list[str]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./yuyue.db"
    secret_key: str = "dev-secret-key"
    access_token_expire_minutes: int = 120
    refresh_token_expire_days: int = 7
    upload_dir: str = "./uploads"
    max_upload_mb: int = 2
    environment: str = "development"
    seed_on_startup: bool = False
    cors_origins: _CorsOrigins = ["http://localhost:5173"]
    host: str = "127.0.0.1"
    port: int = 8000
    frontend_dist: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> list[str]:
        return parse_cors_origins(value)


_WEAK_SECRET_KEYS = frozenset({"dev-secret-key", "change-me-in-production", "REPLACE_WITH_OPENSSL_RAND_HEX_32"})

settings = Settings()

if settings.environment == "production" and settings.secret_key in _WEAK_SECRET_KEYS:
    raise RuntimeError("生产环境必须设置强随机 SECRET_KEY（运行 scripts/install.sh 可自动生成）")
