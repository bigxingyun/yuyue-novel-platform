<div align="center">

# 欲阅 · yuyue-novel-platform

**以短篇小说为核心的多用户在线阅读平台。**

[![CI](https://github.com/bigxingyun/yuyue-novel-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/bigxingyun/yuyue-novel-platform/actions/workflows/ci.yml)
[![Backend Tests](https://img.shields.io/badge/backend%20tests-pytest-0A9EDC?logo=pytest&logoColor=white)](#-测试)
[![Frontend Tests](https://img.shields.io/badge/frontend%20tests-vitest-6DA544?logo=vitest&logoColor=white)](#-测试)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](#-环境依赖-prerequisites)
[![Node.js](https://img.shields.io/badge/node.js-%E2%89%A518-339933?logo=node.js&logoColor=white)](#-环境依赖-prerequisites)
[![Vue](https://img.shields.io/badge/vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

[项目介绍](#-项目介绍) ·
[环境依赖](#-环境依赖-prerequisites) ·
[安装步骤](#-安装步骤-installation) ·
[快速上手](#-快速上手-usage) ·
[许可证](#-许可证-license) ·
[完整文档](./docs/README.md)

</div>

---

## 📖 项目介绍

「欲阅」以短篇小说为核心：读者可全屏阅读并调节字号、主题与翻页方式，评论可精确到段落；作者申请通过后即可发布作品与章节；管理员通过注册码准入与后台完成内容治理。

### 核心功能

| 能力域 | 说明 |
|--------|------|
| **用户体系** | 注册码一次性注册、找回密钥重置密码、JWT 双令牌（Access 2h / Refresh 7d）、封禁、经验与每日签到、阅读头衔（Lv.1–10） |
| **内容消费** | 广场（分类 / 排序 / 搜索 / 分页）、书主页、书架、阅读页、阅读历史 |
| **社交互动** | 段评 / 章评 / 书评三级评论、一级回复、作者置顶、管理员隐藏 |
| **内容创作** | 作者申请与审核、作品与章节 CRUD、发布 / 下架、章节拖拽排序、正文图片块 |
| **平台运营** | 管理后台：用户与角色、注册码 / 找回密钥、作品上下架、作者申请审批、评论治理 |
| **阅读体验** | 全屏阅读、字号与主题切换、翻页模式、进度续读、阅读设置云端同步 |
| **多端适配** | 按 UA 识别 PC / Android / iOS，布局与阅读交互分别分支 |

角色体系：`guest` →（注册码）→ `user` →（申请 + 审核）→ `author`，另有由超管指派的 `admin` 与种子账号 `superadmin`。

### 适用场景

- 📚 **学习与二次开发**：Vue 3 + TypeScript + FastAPI + SQLAlchemy 2.x 的前后端分离完整范例，含 67 个 API 端点、统一响应协议、分层架构与测试体系；
- 🚀 **中小型内容平台原型**：单机单端口即可上线，SQLite 零配置，适合快速验证产品想法；
- ✍️ **短篇创作社区自建**：注册码准入 + 作者审核，适合小范围邀请制运营。

> 技术栈：**Vue 3.5 + TypeScript + Vite 6 + Pinia** ｜ **Python + FastAPI + SQLAlchemy 2.x** ｜ **SQLite** ｜ **JWT (HS256) + bcrypt**

### 目录结构

```
欲阅/
├── backend/           # FastAPI 后端（app/api、models、schemas、services、core）
│   └── tests/         # pytest 测试
├── frontend/          # Vue 3 前端（src/views、stores、api）
├── deploy/            # systemd 单元模板、nginx 示例
├── scripts/           # Ubuntu 部署与运维脚本
├── docs/              # 项目文档（架构 / 数据库 / API / 部署 / 测试）
├── .github/workflows/ # GitHub Actions CI
└── LICENSE            # GPL-3.0
```

---

## 🔧 环境依赖 Prerequisites

### 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows / Linux（开发）；Ubuntu 20.04 / 22.04 / 24.04（生产部署） |
| Python | **3.10+**（CI 覆盖 3.10 / 3.11 / 3.12） |
| Node.js | **18+**（推荐 20 LTS，部署脚本会在低于 18 时自动安装 20 LTS） |
| npm | 随 Node.js 安装（推荐 9+） |
| 磁盘 | 约 500 MB（含 `node_modules` 与虚拟环境） |

### 运行时依赖

后端（[`backend/requirements.txt`](./backend/requirements.txt)）：

| 依赖 | 版本 | 用途 |
|------|------|------|
| `fastapi` | ≥ 0.115.0 | Web 框架与 OpenAPI |
| `uvicorn[standard]` | ≥ 0.32.0 | ASGI 服务器 |
| `sqlalchemy` | ≥ 2.0.0 | ORM |
| `alembic` | ≥ 1.14.0 | 迁移工具（当前以轻量增量补丁为主） |
| `pydantic` / `pydantic-settings` | ≥ 2.0.0 | 校验与配置 |
| `python-jose[cryptography]` | ≥ 3.3.0 | JWT 签发与校验 |
| `passlib[bcrypt]` + `bcrypt` | ≥ 1.7.4 / ≥4.0.0,<4.1.0 | 密码哈希（**bcrypt 上限锁定 4.1.0**） |
| `python-multipart` | ≥ 0.0.12 | 表单与文件上传 |
| `aiofiles` | ≥ 24.0.0 | 异步文件读写 |

前端（[`frontend/package.json`](./frontend/package.json)）：`vue@^3.5`、`vue-router@^4.4`、`pinia@^2.2`、`axios@^1.7`、`@phosphor-icons/vue@^2.2`；开发依赖 `vite@^6`、`typescript@~5.6`、`vue-tsc@^2.1`、`vitest@^3`。

### 第三方服务

**无需任何第三方服务。** 数据库为本地 SQLite 文件，图片存储为本地 `uploads/` 目录，无 Redis、无对象存储、无外部 API Key。

### 环境变量

复制 [`backend/.env.example`](./backend/.env.example) 为 `backend/.env` 后按需修改：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DATABASE_URL` | `sqlite:///./yuyue.db` | 数据库连接串 |
| `SECRET_KEY` | `change-me-in-production` | JWT 签名密钥，**生产环境必须更换** |
| `ENVIRONMENT` | `development` | `production` 时禁止执行 `reset_db` |
| `SEED_ON_STARTUP` | `false` | 启动时是否自动写入演示数据 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | Access Token 有效期 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh Token 有效期 |
| `UPLOAD_DIR` | `./uploads` | 上传文件目录 |
| `MAX_UPLOAD_MB` | `2` | 单张图片大小上限 |
| `CORS_ORIGINS` | `http://localhost:5173` | 允许的跨域来源 |

---

## 🚀 安装步骤 Installation

### 0. 克隆仓库

```bash
git clone https://github.com/bigxingyun/yuyue-novel-platform.git
cd yuyue-novel-platform
```

### 1. 后端

> Windows 下激活命令为 `.venv\Scripts\activate`（PowerShell：`.venv\Scripts\Activate.ps1`）。

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

准备好数据（建表 + 写入演示数据）：

```bash
python -m app.seed_test
```

启动服务：

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- 首次启动会创建 `backend/yuyue.db` 并执行增量 schema 补丁（`run_schema_migrations`）；
- 交互式 API 文档：<http://localhost:8000/docs>（API 前缀 `/api/v1`）。

### 2. 前端

另开一个终端：

```bash
cd frontend
npm install                        # 严格按锁文件安装可用 npm ci
npm run dev
```

访问 <http://localhost:5173>。Vite 已把 `/api` 与 `/uploads` 代理到 `http://127.0.0.1:8000`，本地无需配置跨域。

### 3. 验证安装

```bash
cd backend
PYTHONPATH=. python scripts/verify_seed.py   # Windows PowerShell: $env:PYTHONPATH='.'; python scripts/verify_seed.py
```

该脚本会走一遍真实登录、广场列表、章节分块与注册码校验，成功时以 `VERIFY DONE` 结束，并输出 `placeholder_chapters=0`（表示章节正文已填充，无「待更新」占位）。

### 4. 测试

```bash
# 后端（pytest）
cd backend && python -m pytest -q        # 当前 12 项用例通过

# 前端（vitest，含 parseChapterBlocks 正文分块）
cd frontend && npm test

# 前端类型检查与生产构建
cd frontend && npm run build       # vue-tsc -b && vite build
```

后端测试覆盖注册码原子消费、鉴权与密钥、章节正文分块、签到与个人资料、管理后台功能等场景（见 [`backend/tests/`](./backend/tests/)）。CI 配置见 [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)。

### 5. 生产部署（Ubuntu，可选）

单端口模式，无需 Nginx。脚本位于 [`scripts/`](./scripts/)：

```bash
chmod +x scripts/*.sh
sudo bash scripts/install.sh --with-seed --port 9080
bash scripts/status.sh
```

访问 `http://<公网IP>:9080`（前端、`/api/v1`、`/uploads` 同端口），详见 [`docs/09-部署与运维.md`](./docs/09-部署与运维.md)。

> 用 WinSCP 等工具上传后若报 `$'\r': command not found`，脚本换行符需转为 LF：
> `sed -i 's/\r$//' scripts/*.sh scripts/lib/*.sh`

---

## ⚡ 快速上手 Usage

### 最小可用示例：1 分钟跑通

```bash
# 终端 1 —— 后端
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# 终端 2 —— 前端
cd frontend && npm run dev
```

打开 <http://localhost:5173>，用演示账号登录即可体验完整链路。

### 演示账号与注册码

登录时「账号」字段填**昵称**（后端按 `nickname` 匹配，也支持纯数字的用户 ID）：

| 账号（昵称） | 密码 | 角色 |
|------|------|------|
| `superadmin` | `super123` | 超级用户（可分派管理员） |
| `admin` | `admin123` | 管理员 |
| `reader` | `test123` | 读者 |
| `晚风读者` | `123456` | 读者（含书架、段评、阅读进度） |
| `林暮` | `test123` | 作者（主测账号，含已发布作品与章节） |
| `applicant` | `test123` | 读者（有待审核的作者申请） |
| `banned` | `test123` | 读者（已封禁，登录返回 40301） |

注册码：`YUYUE-DEMO-2026`、`YUYUE-TEST-READ`（永久有效）、`YUYUE-TEST-EXP`（30 天有效）

> 以上数据由 `python -m app.seed_test` 写入，仅供本地演示；`ENVIRONMENT=production` 时该命令会被拒绝执行。

### API 调用示例

所有业务接口以 `/api/v1` 为前缀，统一响应格式 `{ code, message, data }`，分页数据形如 `{ items, total, page, page_size }`。

**登录获取令牌：**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account": "reader", "password": "test123"}'
```

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "access_token": "<JWT>",
    "refresh_token": "<JWT>",
    "token_type": "bearer"
  }
}
```

**浏览广场（公开接口，无需登录；`sort` 支持 `updated`（默认）/ `words`，另支持 `category`、`keyword`）：**

```bash
curl "http://127.0.0.1:8000/api/v1/books?page=1&page_size=10&sort=words"
```

**读取当前用户资料（需登录）：**

```bash
curl http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

**前端调用（`src/api` 层已封装 axios 拦截器，自动附加 Token 并做 `snake_case` ↔ `camelCase` 字段转换）：**

```ts
// src/api/books.ts
import { request } from '@/api/request'
import type { PageResult } from '@/types/api'
import type { BookListItem } from '@/types/book'

export function fetchBookList(params: {
  page?: number
  pageSize?: number
  category?: string
  keyword?: string
  sort?: 'updated' | 'words'
}) {
  return request<PageResult<BookListItem>>({
    method: 'GET',
    url: '/books',
    params,
  })
}

// 业务层直接用 camelCase，边界处（request 拦截器）自动转为 snake_case
const result = await fetchBookList({ page: 1, pageSize: 10, sort: 'words' })
console.log(result.items, result.total)
```

### 关键接口一览

| 前缀 | 说明 |
|------|------|
| `POST /auth/login` `/refresh` `/register` `/recover` `/logout` | 认证与会话 |
| `GET /books` `/{id}` `/categories` `/{id}/comments` | 广场、详情、更新日志、书评 |
| `GET /chapters/{id}` | 章节正文（含正文块与图片块） |
| `GET/POST /comments/paragraph` `/chapter` | 段评与章评 |
| `GET/POST/DELETE /bookshelf` | 书架 |
| `GET/PUT /reading/progress`、`GET /reading/history` | 阅读进度与历史 |
| `POST /profile/check-in`、`GET /profile/titles` | 签到、经验、阅读头衔、作者申请 |
| `/author/books`、`/author/chapters/{id}` | 作者作品与章节 CRUD |
| `/admin/users` `/keys` `/books` `/applications` `/comments` | 管理后台 |

完整端点与字段见 [`docs/08-API接口文档.md`](./docs/08-API接口文档.md)，或运行后直接查看 <http://localhost:8000/docs>。

---

## 📄 许可证 License

本项目基于 **GNU General Public License v3.0（GPL-3.0）** 开源，完整协议文本见 [LICENSE](./LICENSE)。

```
Copyright (C) 2026 行云 (bigxingyun) <https://github.com/bigxingyun/yuyue-novel-platform>

本程序是自由软件：你可以依据自由软件基金会发布的 GNU 通用公共许可证条款
（第三版，或你选择的任何更新版本）重新发布和/或修改它。

本程序分发的目的是希望它有用，但不提供任何担保，甚至不包含适销性或
特定用途适用性的默示担保。详见 GNU 通用公共许可证。
```

GPL-3.0 意味着：你可以自由使用、修改、分发本项目（包括商业用途），但**衍生作品必须以相同协议开源**，且需保留版权声明。若需在其他协议下使用，请联系作者。

---

## 文档

- 文档索引与阅读顺序：[docs/README.md](./docs/README.md)
- 开发规范（命名、响应协议、错误码）：[docs/CONVENTIONS.md](./docs/CONVENTIONS.md)
- 产品需求与技术规格：[欲阅需求分析.md](./欲阅需求分析.md)

如有问题或建议，欢迎提交 Issue。
