"""个人中心路由。"""

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ok
from app.schemas.profile import AuthorApplicationRequest, ReaderSettingsUpdate
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/check-in")
def check_in(db: DbSession, user: CurrentUser):
    return ok(profile_service.check_in(db, user))


@router.get("/check-in/status")
def check_in_status(db: DbSession, user: CurrentUser):
    return ok(profile_service.check_in_status(db, user.id))


@router.get("/exp-logs")
def exp_logs(db: DbSession, user: CurrentUser, page: int = 1, page_size: int = 20):
    return ok(profile_service.list_exp_logs(db, user.id, page, page_size))


@router.post("/author-application")
def submit_application(body: AuthorApplicationRequest, db: DbSession, user: CurrentUser):
    return ok(profile_service.submit_author_application(db, user, body.reason))


@router.get("/author-application")
def get_application(db: DbSession, user: CurrentUser):
    return ok(profile_service.get_author_application(db, user.id))


@router.get("/reader-settings")
def get_reader_settings(db: DbSession, user: CurrentUser):
    return ok({"settings": profile_service.get_reader_settings(db, user.id)})


@router.put("/reader-settings")
def update_reader_settings(body: ReaderSettingsUpdate, db: DbSession, user: CurrentUser):
    return ok({"settings": profile_service.update_reader_settings(db, user.id, body.settings)})


@router.get("/titles")
def get_titles(db: DbSession, user: CurrentUser):
    return ok(profile_service.get_titles(db, user.id))
