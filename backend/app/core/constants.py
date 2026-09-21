"""项目级常量与枚举 — 命名与取值的唯一来源（后端）。"""

from enum import Enum


# ---------------------------------------------------------------------------
# 用户与权限
# ---------------------------------------------------------------------------

class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    AUTHOR = "author"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class UserStatus(str, Enum):
    ACTIVE = "active"
    BANNED = "banned"


# ---------------------------------------------------------------------------
# 内容与评论
# ---------------------------------------------------------------------------

class BookStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"


class KeyStatus(str, Enum):
    UNUSED = "unused"
    USED = "used"
    EXPIRED = "expired"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CommentType(str, Enum):
    PARAGRAPH = "paragraph"
    CHAPTER = "chapter"
    BOOK = "book"


class ExpSource(str, Enum):
    CHECK_IN = "check_in"
    READ = "read"
    COMMENT = "comment"


# ---------------------------------------------------------------------------
# 设备类型（UA）
# ---------------------------------------------------------------------------

class DeviceType(str, Enum):
    DESKTOP = "desktop"
    ANDROID = "android"
    IOS = "ios"


# ---------------------------------------------------------------------------
# 分页
# ---------------------------------------------------------------------------

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 50

BOOK_CATEGORIES = ["玄幻", "都市", "科幻", "悬疑", "言情", "历史", "其他"]

# 经验头衔等级（累计经验门槛）
TITLE_LEVELS = [
    {"level": 1, "title": "门外读者", "min_exp": 0},
    {"level": 2, "title": "初窥门径", "min_exp": 30},
    {"level": 3, "title": "书香初染", "min_exp": 80},
    {"level": 4, "title": "闲章散笔", "min_exp": 150},
    {"level": 5, "title": "夜读者", "min_exp": 250},
    {"level": 6, "title": "书斋常客", "min_exp": 400},
    {"level": 7, "title": "字里行间", "min_exp": 600},
    {"level": 8, "title": "万卷书生", "min_exp": 900},
    {"level": 9, "title": "阅尽千帆", "min_exp": 1300},
    {"level": 10, "title": "欲阅宗师", "min_exp": 1800},
]


# ---------------------------------------------------------------------------
# 业务错误码（与 docs/CONVENTIONS.md §3.5 一致）
# ---------------------------------------------------------------------------

class ErrorCode:
    OK = 0

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500

    REGISTRATION_KEY_INVALID = 40001
    NICKNAME_TAKEN = 40002

    TOKEN_EXPIRED = 40101

    ACCOUNT_BANNED = 40301
    AUTHOR_REQUIRED = 40302
    ADMIN_REQUIRED = 40303

    BOOK_NOT_FOUND = 40401
    CHAPTER_NOT_FOUND = 40402

    ALREADY_CHECKED_IN = 40901
