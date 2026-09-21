"""文件上传路由。"""



from fastapi import APIRouter, UploadFile



from app.api.deps import CurrentUser

from app.schemas.common import ok

from app.services import upload_service



router = APIRouter(prefix="/upload", tags=["upload"])





@router.post("/image")

def upload_image(file: UploadFile, _user: CurrentUser):

    url = upload_service.save_image(file)

    return ok({"url": url})


