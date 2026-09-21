"""修复存量章节正文 marker 并重算字数。

用法（在 backend 目录）:
    python -m app.seed_repair
"""

from app.seed import repair_chapter_content

if __name__ == "__main__":
    count = repair_chapter_content()
    print(f"已修复 {count} 个章节并重算书籍字数")
