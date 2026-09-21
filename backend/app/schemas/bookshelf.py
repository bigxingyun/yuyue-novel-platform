"""书架与阅读 Schema。"""

from pydantic import BaseModel, Field


class BookshelfItemOut(BaseModel):
    id: int
    title: str
    author: str
    cover: str
    word_count: int
    updated_at: str
    progress: float
    chapter_id: int | None = None
    chapter_title: str | None = None
    read_at: str | None = None


class AddBookshelfRequest(BaseModel):
    book_id: int


class UpdateProgressRequest(BaseModel):
    book_id: int
    chapter_id: int
    offset: float = Field(ge=0, le=1)


class ReadingHistoryOut(BaseModel):
    id: int
    book_id: int
    chapter_id: int
    title: str
    cover: str
    chapter_title: str
    read_at: str
