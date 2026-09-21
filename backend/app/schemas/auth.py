"""认证与用户 Schema。"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    account: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=6, max_length=64)


class RegisterVerifyRequest(BaseModel):
    registration_key: str = Field(min_length=4, max_length=32)


class RegisterRequest(BaseModel):
    registration_key: str = Field(min_length=4, max_length=32)
    nickname: str = Field(min_length=2, max_length=20)
    password: str = Field(min_length=6, max_length=64)
    avatar: str | None = None


class RecoverRequest(BaseModel):
    account: str = Field(min_length=1, max_length=20)
    recovery_key: str = Field(min_length=4, max_length=32)
    new_password: str = Field(min_length=6, max_length=64)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    nickname: str
    avatar: str
    role: str
    exp: int
    level: int = 1
    title: str = "门外读者"
    exp_in_level: int = 0
    exp_to_next: int = 0

    model_config = {"from_attributes": True}


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=6, max_length=64)
    new_password: str = Field(min_length=6, max_length=64)


class UpdateProfileRequest(BaseModel):
    nickname: str | None = Field(default=None, min_length=2, max_length=20)
    avatar: str | None = None
