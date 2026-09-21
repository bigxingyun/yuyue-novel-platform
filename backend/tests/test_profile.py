"""资料修改相关测试。"""

import uuid

from app.core.security import create_access_token, hash_password
from app.database import SessionLocal
from app.models import User
from app.services import profile_service
from fastapi.testclient import TestClient

from app.main import app


def _auth_header(user_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user_id)}"}


def test_update_avatar_only_keeps_nickname():
    db = SessionLocal()
    nickname = f"pt_{uuid.uuid4().hex[:6]}"
    user = User(
        nickname=nickname,
        password_hash=hash_password("test123"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    client = TestClient(app)
    r = client.patch(
        "/api/v1/users/me",
        json={"nickname": nickname, "avatar": "http://example.com/new.png"},
        headers=_auth_header(user.id),
    )
    assert r.status_code == 200
    assert r.json()["code"] == 0
    assert r.json()["data"]["nickname"] == nickname
    assert r.json()["data"]["avatar"] == "http://example.com/new.png"

    db.refresh(user)
    assert user.nickname == nickname
    assert user.avatar == "http://example.com/new.png"

    db.delete(user)
    db.commit()
    db.close()


def test_update_profile_service_avatar_only():
    db = SessionLocal()
    nickname = f"st_{uuid.uuid4().hex[:6]}"
    user = User(
        nickname=nickname,
        password_hash=hash_password("test123"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    out = profile_service.update_profile(db, user, nickname, "http://a.test/x.png")
    assert out.nickname == nickname
    assert out.avatar == "http://a.test/x.png"

    db.delete(user)
    db.commit()
    db.close()
