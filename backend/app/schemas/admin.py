"""管理后台 Schema。"""

from pydantic import BaseModel, Field


class AdminUserOut(BaseModel):
    id: int
    nickname: str
    role: str
    status: str
    exp: int
    created_at: str


class UpdateUserStatusRequest(BaseModel):
    status: str = Field(pattern="^(active|banned)$")


class UpdateUserRoleRequest(BaseModel):
    role: str


class GenerateKeysRequest(BaseModel):
    count: int = Field(default=1, ge=1, le=50)
    expire_days: int | None = Field(default=None, ge=1, le=365)


class RegistrationKeyOut(BaseModel):
    id: int
    code: str
    status: str
    used_by: int | None
    created_at: str
    expires_at: str | None = None


class RecoveryKeyOut(BaseModel):
    code: str
    user_id: int
    nickname: str


class AdminBookOut(BaseModel):
    id: int
    title: str
    author: str
    category: str
    status: str
    admin_delisted: bool = False
    word_count: int
    updated_at: str


class UpdateBookStatusRequest(BaseModel):
    status: str = Field(pattern="^(published|unpublished)$")


class AuthorApplicationAdminOut(BaseModel):
    id: int
    user_id: int
    nickname: str
    reason: str
    status: str
    created_at: str
    review_note: str | None = None


class ReviewApplicationRequest(BaseModel):
    status: str = Field(pattern="^(approved|rejected)$")
    review_note: str | None = Field(default=None, max_length=500)


class AdminCommentOut(BaseModel):
    id: int
    type: str
    user: str
    user_id: int
    avatar: str = ""
    content: str
    book_title: str
    book_id: int
    chapter_title: str | None = None
    paragraph_index: int | None = None
    is_hidden: bool = False
    created_at: str


class AdminChapterOut(BaseModel):
    id: int
    title: str
    word_count: int
    sort_order: int
    updated_at: str


class AdminChapterDetailOut(AdminChapterOut):
    book_id: int
    book_title: str
    content: str


class AdminUpdateChapterRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, max_length=50000)
