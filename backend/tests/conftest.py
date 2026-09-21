# pytest 配置与 fixtures

import pytest

from app.database import engine, run_schema_migrations


@pytest.fixture(scope="session", autouse=True)
def apply_schema_migrations():
    run_schema_migrations(engine)
