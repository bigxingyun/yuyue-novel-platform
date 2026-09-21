"""应用配置。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    cors_origins: list[str] = ["http://localhost:5173"]
    host: str = "127.0.0.1"
    port: int = 8000
    frontend_dist: str = ""


_WEAK_SECRET_KEYS = frozenset({"dev-secret-key", "change-me-in-production", "REPLACE_WITH_OPENSSL_RAND_HEX_32"})

settings = Settings()

if settings.environment == "production" and settings.secret_key in _WEAK_SECRET_KEYS:
    raise RuntimeError("生产环境必须设置强随机 SECRET_KEY（运行 scripts/install.sh 可自动生成）")
