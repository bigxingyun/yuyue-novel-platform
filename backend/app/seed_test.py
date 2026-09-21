"""重置并填充测试数据。

用法（在 backend 目录）:
    python -m app.seed_test
"""

from app.seed import reset_db

if __name__ == "__main__":
    reset_db()
