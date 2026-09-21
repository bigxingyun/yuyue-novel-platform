"""验证 seed 数据是否完整。"""

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import AuthorApplication, Book, Chapter, RegistrationKey, User

client = TestClient(app)
db = SessionLocal()

books = db.query(Book).count()
chapters = db.query(Chapter).count()
users = db.query(User).count()
apps = db.query(AuthorApplication).filter_by(status="pending").count()
keys = db.query(RegistrationKey).filter_by(status="unused").count()
placeholder = db.query(Chapter).filter(Chapter.content.like("%待更新%")).count()
print(f"books={books} chapters={chapters} users={users} pending_apps={apps} unused_keys={keys}")
print(f"placeholder_chapters={placeholder} (should be 0)")

cases = [
    ("superadmin", "super123", 0),
    ("admin", "admin123", 0),
    ("reader", "test123", 0),
    ("林暮", "test123", 0),
    ("banned", "test123", 40301),
]
for nick, pwd, expect_code in cases:
    r = client.post("/api/v1/auth/login", json={"account": nick, "password": pwd})
    body = r.json()
    code = body.get("code", -1)
    role = body["data"]["user"]["role"] if code == 0 else "-"
    status = "OK" if code == expect_code else "FAIL"
    print(f"login {nick}: code={code} role={role} {status}")

r = client.get("/api/v1/books?page=1&page_size=20")
print(f"square published books={r.json()['data']['total']}")

r = client.get("/api/v1/chapters/1")
content = r.json()["data"]["content"]
paras = len([p for p in content.split("\n\n") if p.strip()])
print(f"chapter1 paragraphs={paras}")

r = client.post("/api/v1/auth/register/verify", json={"registration_key": "YUYUE-DEMO-2026"})
print(f"verify YUYUE-DEMO-2026: code={r.json()['code']}")

db.close()
print("VERIFY DONE")
