"""初始化数据库与测试演示数据。"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.constants import ApplicationStatus, BookStatus, ExpSource, KeyStatus, UserRole, UserStatus
from app.core.security import hash_password
from app.data.test_stories import CHAPTER_TEXTS, DRAFT_CHAPTER, chapter_content, count_words
from app.config import settings
from app.database import SessionLocal, engine, run_schema_migrations
from app.models import (
    AuthorApplication,
    Base,
    Book,
    BookComment,
    Bookshelf,
    Chapter,
    ChapterComment,
    CheckIn,
    ExpLog,
    ParagraphComment,
    ReadingProgress,
    RegistrationKey,
    UpdateLog,
    User,
)

# ---------------------------------------------------------------------------
# 测试账号（登录：昵称 + 密码）
# ---------------------------------------------------------------------------
TEST_PASSWORD = "test123"
ADMIN_PASSWORD = "admin123"
SUPER_PASSWORD = "super123"
DEMO_READER_PASSWORD = "123456"

BOOKS_DATA = [
    {
        "title": "雨夜列车",
        "author_key": "林暮",
        "category": "悬疑",
        "description": "一列只在雨夜出现的列车，载着十二位互不相识的乘客。每到一站，车厢里就会少一个人，而月台上总会多出一封没有署名的信。",
        "cover": "https://picsum.photos/seed/yuyue-rain-train/400/560",
        "updated_at": "2026-06-20",
        "chapters": ["第一节 候车室", "第二节 空座", "第三节 匿名信"],
    },
    {
        "title": "城北旧事",
        "author_key": "沈砚",
        "category": "都市",
        "description": "旧城改造的前夜，便利店老板在拆迁墙上发现一张二十年前的合影。",
        "cover": "https://picsum.photos/seed/yuyue-city-north/400/560",
        "updated_at": "2026-06-18",
        "chapters": ["第一章 便利店", "第二章 拆迁办"],
    },
    {
        "title": "星尘邮局",
        "author_key": "顾遥",
        "category": "科幻",
        "description": "在轨道空间站尽头，有一家只接收「迟到的信」的邮局。",
        "cover": "https://picsum.photos/seed/yuyue-star-post/400/560",
        "updated_at": "2026-06-15",
        "chapters": ["序章 轨道尽头", "第一封 迟到的道歉"],
    },
    {
        "title": "春山不见",
        "author_key": "白芷",
        "category": "言情",
        "description": "她每年春天回一次山里，去一间早已废弃的茶寮。",
        "cover": "https://picsum.photos/seed/yuyue-spring-mountain/400/560",
        "updated_at": "2026-06-12",
        "chapters": ["壹 茶寮", "贰 旧路"],
    },
    {
        "title": "时间当铺",
        "author_key": "程野",
        "category": "玄幻",
        "description": "可以用记忆换时间的当铺，营业时间不写在门口。",
        "cover": "https://picsum.photos/seed/yuyue-time-shop/400/560",
        "updated_at": "2026-06-10",
        "chapters": ["卷一·开铺", "卷一·第一笔交易"],
    },
    {
        "title": "江声录",
        "author_key": "周渡",
        "category": "历史",
        "description": "口述史整理者在江边采访最后一位摆渡人。",
        "cover": "https://picsum.photos/seed/yuyue-river-voice/400/560",
        "updated_at": "2026-06-08",
        "chapters": ["引子 渡口", "第一记 潮信"],
    },
    {
        "title": "午后三点半",
        "author_key": "苏浅",
        "category": "言情",
        "description": "阅报栏拆除前的最后一个下午，一盒草莓牛奶的告别。",
        "cover": "https://picsum.photos/seed/yuyue-afternoon/400/560",
        "updated_at": "2026-06-22",
        "chapters": ["全文"],
    },
    {
        "title": "电梯停在一层",
        "author_key": "韩非",
        "category": "悬疑",
        "description": "凌晨一点，电梯多开出的一层，和父亲有关的工牌。",
        "cover": "https://picsum.photos/seed/yuyue-elevator/400/560",
        "updated_at": "2026-06-21",
        "chapters": ["全文"],
    },
    {
        "title": "最后一家唱片店",
        "author_key": "陆声",
        "category": "都市",
        "description": "商场负一层即将关门的唱片店，卡带里录着失联友人的声音。",
        "cover": "https://picsum.photos/seed/yuyue-record/400/560",
        "updated_at": "2026-06-19",
        "chapters": ["全文"],
    },
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    run_schema_migrations(engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        if not settings.seed_on_startup:
            return
        _seed(db)
    finally:
        db.close()


def reset_db() -> None:
    """清空并重新填充测试数据。"""
    if settings.environment == "production":
        raise RuntimeError("生产环境禁止执行 reset_db，请改用 migration 或手动维护数据")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    run_schema_migrations(engine)
    db = SessionLocal()
    try:
        _seed(db)
    finally:
        db.close()


def repair_chapter_content() -> int:
    """规范化存量章节 content 并重算字数（开发/维护用）。"""
    from sqlalchemy import func

    from app.utils.chapter_content import normalize_chapter_content

    db = SessionLocal()
    repaired = 0
    try:
        for chapter in db.query(Chapter).all():
            raw = chapter.content or ""
            if not raw.strip():
                if chapter.word_count != 0:
                    chapter.word_count = 0
                    repaired += 1
                continue
            try:
                normalized = normalize_chapter_content(raw)
            except ValueError:
                continue
            words = len(normalized.replace("\n", "").replace(" ", ""))
            if normalized != raw or chapter.word_count != words:
                chapter.content = normalized
                chapter.word_count = words
                repaired += 1
        for book in db.query(Book).all():
            total = (
                db.query(func.coalesce(func.sum(Chapter.word_count), 0))
                .filter(Chapter.book_id == book.id)
                .scalar()
            )
            book.word_count = int(total or 0)
        db.commit()
    finally:
        db.close()
    return repaired


def _add_user(
    db: Session,
    nickname: str,
    password: str,
    role: str,
    *,
    exp: int = 0,
    status: str = UserStatus.ACTIVE.value,
) -> User:
    user = User(
        nickname=nickname,
        password_hash=hash_password(password),
        avatar=f"https://api.dicebear.com/7.x/notionists/svg?seed={nickname}",
        role=role,
        exp=exp,
        status=status,
    )
    db.add(user)
    db.flush()
    return user


def _seed(db: Session) -> None:
    superadmin = _add_user(db, "superadmin", SUPER_PASSWORD, UserRole.SUPERADMIN.value, exp=999)
    admin = _add_user(db, "admin", ADMIN_PASSWORD, UserRole.ADMIN.value, exp=500)
    reader = _add_user(db, "reader", TEST_PASSWORD, UserRole.USER.value, exp=860)
    demo = _add_user(db, "晚风读者", DEMO_READER_PASSWORD, UserRole.USER.value, exp=1280)
    applicant = _add_user(db, "applicant", TEST_PASSWORD, UserRole.USER.value, exp=120)
    _add_user(db, "banned", TEST_PASSWORD, UserRole.USER.value, status=UserStatus.BANNED.value)

    # 作者账号：林暮 为主测作者（test123）
    author_map: dict[str, User] = {}
    primary_author = _add_user(db, "林暮", TEST_PASSWORD, UserRole.AUTHOR.value, exp=2400)
    author_map["林暮"] = primary_author

    db.add_all(
        [
            RegistrationKey(code="YUYUE-DEMO-2026", status=KeyStatus.UNUSED.value, created_by=admin.id),
            RegistrationKey(code="YUYUE-TEST-READ", status=KeyStatus.UNUSED.value, created_by=admin.id),
            RegistrationKey(
                code="YUYUE-TEST-EXP",
                status=KeyStatus.UNUSED.value,
                created_by=admin.id,
                expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30),
            ),
        ],
    )

    db.add(
        AuthorApplication(
            user_id=applicant.id,
            reason="我在其它平台连载过两部短篇，希望在欲阅发表实验性系列作品，并参与段评互动功能的打磨。",
            status=ApplicationStatus.PENDING.value,
        ),
    )

    today = date.today()
    db.add_all(
        [
            CheckIn(
                user_id=demo.id,
                fortune_text="今日宜读书，忌熬夜。",
                exp_gained=12,
                check_date=today,
            ),
            CheckIn(
                user_id=reader.id,
                fortune_text="翻开一页，遇见未知的自己。",
                exp_gained=8,
                check_date=today,
            ),
        ],
    )
    db.add_all(
        [
            ExpLog(user_id=demo.id, source=ExpSource.CHECK_IN.value, amount=12),
            ExpLog(user_id=demo.id, source=ExpSource.READ.value, amount=15),
            ExpLog(user_id=demo.id, source=ExpSource.COMMENT.value, amount=5),
            ExpLog(user_id=reader.id, source=ExpSource.CHECK_IN.value, amount=8),
            ExpLog(user_id=reader.id, source=ExpSource.READ.value, amount=10),
        ],
    )

    first_chapter_id: int | None = None
    rain_book_id: int | None = None

    for book_data in BOOKS_DATA:
        author_key = book_data["author_key"]
        if author_key not in author_map:
            author_map[author_key] = _add_user(
                db,
                author_key,
                TEST_PASSWORD,
                UserRole.AUTHOR.value,
                exp=800,
            )
        author = author_map[author_key]

        total_words = 0
        chapter_specs: list[tuple[str, str, int]] = []
        for ch_title in book_data["chapters"]:
            content = chapter_content(book_data["title"], ch_title)
            words = count_words(content)
            total_words += words
            chapter_specs.append((ch_title, content, words))

        book = Book(
            title=book_data["title"],
            author_id=author.id,
            description=book_data["description"],
            cover=book_data["cover"],
            category=book_data["category"],
            word_count=total_words,
            status=BookStatus.PUBLISHED.value,
            updated_at=datetime.strptime(book_data["updated_at"], "%Y-%m-%d"),
        )
        db.add(book)
        db.flush()
        if book_data["title"] == "雨夜列车":
            rain_book_id = book.id

        for idx, (ch_title, content, words) in enumerate(chapter_specs):
            chapter = Chapter(
                book_id=book.id,
                title=ch_title,
                content=content,
                word_count=words,
                sort_order=idx + 1,
            )
            db.add(chapter)
            db.flush()
            if first_chapter_id is None:
                first_chapter_id = chapter.id
            db.add(
                UpdateLog(
                    book_id=book.id,
                    chapter_id=chapter.id,
                    added_words=words,
                    created_at=datetime.strptime(book_data["updated_at"], "%Y-%m-%d"),
                ),
            )

    # 林暮的草稿书（测试发布/下架/删书）
    draft_book = Book(
        title="灯下草稿",
        author_id=primary_author.id,
        description="作者测试用草稿，含未发布章节。",
        cover="https://picsum.photos/seed/yuyue-draft/400/560",
        category="其他",
        word_count=count_words(DRAFT_CHAPTER),
        status=BookStatus.DRAFT.value,
        updated_at=datetime.now(),
    )
    db.add(draft_book)
    db.flush()
    db.add(
        Chapter(
            book_id=draft_book.id,
            title="楔子",
            content=DRAFT_CHAPTER,
            word_count=count_words(DRAFT_CHAPTER),
            sort_order=1,
        ),
    )

    db.flush()

    if first_chapter_id and rain_book_id:
        cc1 = ChapterComment(
            chapter_id=first_chapter_id,
            user_id=demo.id,
            content="检票员那句台词太绝了，读完愣了好几秒。",
        )
        db.add(cc1)
        db.flush()
        db.add(
            ChapterComment(
                chapter_id=first_chapter_id,
                user_id=primary_author.id,
                content="感谢阅读。第四节的故事，会在下一卷展开。",
                is_pinned=True,
            ),
        )
        db.add_all(
            [
                ParagraphComment(
                    chapter_id=first_chapter_id,
                    paragraph_index=0,
                    user_id=demo.id,
                    content="「另一层时间」这个意象好棒。",
                ),
                ParagraphComment(
                    chapter_id=first_chapter_id,
                    paragraph_index=2,
                    user_id=reader.id,
                    content="第三节再来打卡，氛围太压抑了。",
                ),
            ],
        )
        db.add_all(
            [
                BookComment(
                    book_id=rain_book_id,
                    user_id=demo.id,
                    content="适合雨夜读，氛围感拉满。",
                ),
                BookComment(
                    book_id=rain_book_id,
                    user_id=reader.id,
                    content="第三节的转折写得太好了。",
                ),
            ],
        )
        db.add_all(
            [
                Bookshelf(user_id=demo.id, book_id=rain_book_id),
                Bookshelf(user_id=reader.id, book_id=rain_book_id),
            ],
        )
        ch2 = (
            db.query(Chapter)
            .filter(Chapter.book_id == rain_book_id, Chapter.sort_order == 2)
            .first()
        )
        if ch2:
            db.add_all(
                [
                    ReadingProgress(
                        user_id=demo.id,
                        book_id=rain_book_id,
                        chapter_id=ch2.id,
                        offset=0.38,
                    ),
                    ReadingProgress(
                        user_id=reader.id,
                        book_id=rain_book_id,
                        chapter_id=first_chapter_id,
                        offset=0.12,
                    ),
                ],
            )

    db.commit()

    _print_seed_summary()


def _print_seed_summary() -> None:
    lines = [
        "",
        "=" * 56,
        "  欲阅 · 测试数据已就绪",
        "=" * 56,
        "",
        "  账号（昵称登录）    密码        角色",
        "  ─────────────────────────────────────────",
        f"  superadmin          {SUPER_PASSWORD:<10}  超管",
        f"  admin               {ADMIN_PASSWORD:<10}  管理员",
        f"  reader              {TEST_PASSWORD:<10}  普通读者",
        f"  晚风读者            {DEMO_READER_PASSWORD:<10}  普通读者（含评论/书架）",
        f"  林暮                {TEST_PASSWORD:<10}  作者（雨夜列车 + 草稿）",
        f"  applicant           {TEST_PASSWORD:<10}  读者（待审核作者申请）",
        f"  banned              {TEST_PASSWORD:<10}  已封禁",
        "  沈砚/顾遥/…         test123      其它作者（同上密码）",
        "",
        "  注册码",
        "  ─────────────────────────────────────────",
        "  YUYUE-DEMO-2026     永久有效",
        "  YUYUE-TEST-READ     永久有效",
        "  YUYUE-TEST-EXP      30 天有效",
        "",
        f"  书目 {len(BOOKS_DATA)} 本 · 章节均含完整短文正文",
        "  _guest 无需账号，未登录即可浏览广场_",
        "",
        "  重置数据: cd backend && python -m app.seed_test",
        "  修复正文: cd backend && python -m app.seed_repair",
        "=" * 56,
        "",
    ]
    print("\n".join(lines))
