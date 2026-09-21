"""用户路由。"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import ChangePasswordRequest, UpdateProfileRequest
from app.schemas.common import ok
from app.services import profile_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(user: CurrentUser):
    return ok(profile_service.get_user_out(user))


@router.patch("/me")
def update_me(body: UpdateProfileRequest, db: DbSession, user: CurrentUser):
    return ok(profile_service.update_profile(db, user, body.nickname, body.avatar))


@router.post("/me/password")
def change_password(body: ChangePasswordRequest, db: DbSession, user: CurrentUser):
    profile_service.change_password(db, user, body.old_password, body.new_password)
    return ok(None, message="密码已修改")
