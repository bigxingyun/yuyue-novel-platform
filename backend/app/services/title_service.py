"""用户头衔与等级计算。"""

from dataclasses import dataclass

from app.core.constants import TITLE_LEVELS


@dataclass
class TitleInfo:
    level: int
    title: str
    exp: int
    exp_in_level: int
    exp_to_next: int
    progress: float


def get_title_info(exp: int) -> TitleInfo:
    """根据累计经验计算当前等级与进度。"""
    exp = max(0, exp)
    current = TITLE_LEVELS[0]
    for tier in TITLE_LEVELS:
        if exp >= tier["min_exp"]:
            current = tier
        else:
            break

    level = current["level"]
    title = current["title"]
    exp_in_level = exp - current["min_exp"]

    next_tier = next((t for t in TITLE_LEVELS if t["level"] == level + 1), None)
    if next_tier:
        span = next_tier["min_exp"] - current["min_exp"]
        exp_to_next = next_tier["min_exp"] - exp
        progress = exp_in_level / span if span > 0 else 1.0
    else:
        exp_to_next = 0
        progress = 1.0

    return TitleInfo(
        level=level,
        title=title,
        exp=exp,
        exp_in_level=exp_in_level,
        exp_to_next=exp_to_next,
        progress=min(1.0, max(0.0, progress)),
    )


def list_all_titles(exp: int) -> list[dict]:
    """返回全部头衔及解锁状态。"""
    info = get_title_info(exp)
    return [
        {
            "level": tier["level"],
            "title": tier["title"],
            "min_exp": tier["min_exp"],
            "unlocked": exp >= tier["min_exp"],
            "current": tier["level"] == info.level,
        }
        for tier in TITLE_LEVELS
    ]
