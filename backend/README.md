# 欲阅 · 后端

FastAPI 服务，API 前缀 `/api/v1`。开发前阅读 [docs/CONVENTIONS.md](../docs/CONVENTIONS.md)。

## 分层

```
api/v1 路由 → deps 鉴权 → Service → Model → DB
                ↓
         schemas/common.ApiResponse
```

- 枚举与错误码：`app/core/constants.py`
- 响应包装：`app/schemas/common.py`
- 业务异常：`app/core/exceptions.py`（Service 层 `raise_app()`）
- 路由层不写 SQL，不裸返回 dict

## 启动

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

启动时 `init_db()` 建表；`database.run_schema_migrations()` 对已有库做增量列补丁。

**重置演示数据：**

```bash
python -m app.seed_test
```

`ENVIRONMENT=production` 时 `reset_db` 会拒绝执行。

## 测试账号

| 昵称 | 密码 | 角色 |
|------|------|------|
| superadmin | super123 | 超管 |
| admin | admin123 | 管理员 |
| reader | test123 | 读者 |
| 晚风读者 | 123456 | 读者（含书架、段评、进度） |
| 林暮 | test123 | 作者 |
| applicant | test123 | 读者（待审核作者申请） |
| banned | test123 | 读者（已封禁） |

注册码：`YUYUE-DEMO-2026`、`YUYUE-TEST-READ`、`YUYUE-TEST-EXP`（30 天）

## 模块

| 前缀 | 文件 | 说明 |
|------|------|------|
| `/auth` | `auth.py` | 登录、注册、刷新、找回 |
| `/users` | `users.py` | 当前用户资料、改密 |
| `/books` | `books.py` | 广场、详情、更新日志、书评 |
| `/chapters` | `chapters.py` | 章节正文 |
| `/comments` | `comments.py` | 段评、章评 |
| `/bookshelf` | `bookshelf.py` | 书架 |
| `/reading` | `reading.py` | 进度、历史 |
| `/profile` | `profile.py` | 签到、经验、作者申请、阅读设置 |
| `/author` | `author.py` | 作者作品与章节 CRUD |
| `/upload` | `upload.py` | 图片上传 |
| `/admin/*` | `admin/` | 用户、密钥、书籍、申请、评论审核 |

生产部署见根目录 [README.md](../README.md#ubuntu-生产部署)。

## 目录

| 路径 | 职责 |
|------|------|
| `app/api/` | 路由与 deps |
| `app/models/` | ORM 模型 |
| `app/schemas/` | Pydantic 入参/出参 |
| `app/services/` | 业务逻辑 |
| `app/core/` | 常量、JWT、权限、异常 |
| `app/utils/` | 校验、访问控制等工具 |
| `app/data/` | 运势文案、测试故事文本 |
| `app/seed.py` | 初始化与演示数据 |
| `tests/` | pytest |
