"""时间存储与展示 — 库内统一 UTC naive，接口返回东八区本地时间。"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DISPLAY_TZ = ZoneInfo("Asia/Shanghai")


def now_utc() -> datetime:
    """写入数据库用的 UTC 时间（naive）。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_display_datetime(dt: datetime | None) -> str:
    """将库内 UTC naive 时间格式化为东八区 `YYYY-MM-DD HH:MM`。"""
    if not dt:
        return ""
    aware = dt.replace(tzinfo=timezone.utc)
    return aware.astimezone(DISPLAY_TZ).strftime("%Y-%m-%d %H:%M")


def format_display_date(dt: datetime | None) -> str:
    if not dt:
        return ""
    aware = dt.replace(tzinfo=timezone.utc)
    return aware.astimezone(DISPLAY_TZ).strftime("%Y-%m-%d")
