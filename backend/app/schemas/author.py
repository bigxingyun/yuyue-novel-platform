"""作者端 Schema。"""

from pydantic import BaseModel, Field


class AuthorBookOut(BaseModel):
    id: int
    title: str
    description: str
    cover: str
    category: str
    status: str
    admin_delisted: bool = False
    word_count: int
    chapter_count: int
    updated_at: str


class CreateBookRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    category: str = Field(default="其他", max_length=50)
    cover: str | None = None


class UpdateBookRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = None
    cover: str | None = None


class AuthorChapterOut(BaseModel):
    id: int
    title: str
    word_count: int
    sort_order: int
    updated_at: str


class AuthorChapterDetailOut(AuthorChapterOut):
    content: str


class CreateChapterRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(default="", max_length=50000)


class UpdateChapterRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, max_length=50000)


class ReorderChaptersRequest(BaseModel):
    chapter_ids: list[int] = Field(min_length=1)
