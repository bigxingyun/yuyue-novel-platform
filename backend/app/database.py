"""数据库连接与会话管理。"""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_schema_migrations(db_engine: Engine) -> None:
    inspector = inspect(db_engine)
    with db_engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_migrations ("
                "id INTEGER PRIMARY KEY, version INTEGER NOT NULL)"
            ),
        )
        row = conn.execute(text("SELECT version FROM schema_migrations WHERE id = 1")).fetchone()
        version = int(row[0]) if row else 0
        if version < 1:
            if not row:
                conn.execute(text("INSERT INTO schema_migrations (id, version) VALUES (1, 1)"))
            else:
                conn.execute(text("UPDATE schema_migrations SET version = 1 WHERE id = 1"))
            version = 1
    if not inspector.has_table("users"):
        return
    columns = {col["name"] for col in inspector.get_columns("users")}
    with db_engine.begin() as conn:
        if "reader_settings" not in columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN reader_settings TEXT"))
        if inspector.has_table("books"):
            book_columns = {col["name"] for col in inspector.get_columns("books")}
            if "admin_delisted" not in book_columns:
                conn.execute(text("ALTER TABLE books ADD COLUMN admin_delisted BOOLEAN DEFAULT 0"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
