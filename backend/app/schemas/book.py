"""书籍与章节 Schema。"""

from pydantic import BaseModel, Field


class ChapterBrief(BaseModel):
    id: int
    title: str
    word_count: int


class BookListItem(BaseModel):
    id: int
    title: str
    author: str
    category: str
    cover: str
    word_count: int
    updated_at: str


class UpdateLogOut(BaseModel):
    chapter_id: int
    date: str
    chapter_title: str
    added_words: int


class ReadingProgressOut(BaseModel):
    chapter_id: int
    offset: float


class BookDetailOut(BaseModel):
    id: int
    title: str
    author: str
    author_id: int
    category: str
    description: str
    cover: str
    word_count: int
    updated_at: str
    chapters: list[ChapterBrief]
    progress: ReadingProgressOut | None = None
    in_shelf: bool = False


class TextBlockOut(BaseModel):
    type: str = "text"
    text: str
    paragraph_index: int


class ImageBlockOut(BaseModel):
    type: str = "image"
    url: str
    after_paragraph_index: int


class ChapterOut(BaseModel):
    id: int
    book_id: int
    title: str
    content: str
    paragraphs: list[str]
    blocks: list[TextBlockOut | ImageBlockOut]
    word_count: int


class BookCommentOut(BaseModel):
    id: int
    user: str
    avatar: str
    time: str
    content: str


class CreateBookCommentRequest(BaseModel):
    content: str = Field(min_length=1, max_length=500)
