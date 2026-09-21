"""个人中心 Schema。"""

from pydantic import BaseModel, Field


class CheckInOut(BaseModel):
    fortune_text: str
    exp_gained: int
    exp: int
    leveled_up: bool = False
    new_title: str | None = None
    level: int = 1
    title: str = "门外读者"


class CheckInStatusOut(BaseModel):
    checked_in: bool
    fortune_text: str | None = None


class ExpLogOut(BaseModel):
    id: int
    source: str
    amount: int
    time: str


class AuthorApplicationRequest(BaseModel):
    reason: str = Field(min_length=10, max_length=500)


class AuthorApplicationOut(BaseModel):
    status: str
    reason: str | None = None
    review_note: str | None = None


class ReaderSettingsOut(BaseModel):
    settings: dict | None = None


class ReaderSettingsUpdate(BaseModel):
    settings: dict


class TitleTierOut(BaseModel):
    level: int
    title: str
    min_exp: int
    unlocked: bool
    current: bool


class TitlesOut(BaseModel):
    level: int
    title: str
    exp: int
    exp_in_level: int
    exp_to_next: int
    progress: float
    tiers: list[TitleTierOut]
