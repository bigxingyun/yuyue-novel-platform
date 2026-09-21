# 欲阅 · API 接口文档

| 字段 | 内容 |
|------|------|
| 文档类型 | 接口文档（全部端点、参数、权限、返回结构） |
| 版本 | v1.0 |
| 最后更新 | 2026-07-03 |
| 数据来源 | `backend/app/api/v1/**` 路由代码（以代码为准，共 67 个业务端点） |

> 交互式文档：本地/开发环境启动后端后访问 `/docs`（OpenAPI Swagger UI）。本文档为静态速查版。

---

## 目录

1. [通用约定](#1-通用约定)
2. [认证 /auth](#2-认证-auth)
3. [用户 /users](#3-用户-users)
4. [书籍 /books](#4-书籍-books)
5. [章节 /chapters](#5-章节-chapters)
6. [评论 /comments](#6-评论-comments)
7. [书架 /bookshelf](#7-书架-bookshelf)
8. [阅读 /reading](#8-阅读-reading)
9. [个人 /profile](#9-个人-profile)
10. [作者 /author](#10-作者-author)
11. [上传 /upload](#11-上传-upload)
12. [管理 /admin](#12-管理-admin)
13. [其他端点](#13-其他端点)
14. [鉴权依赖与分页](#14-鉴权依赖与分页)

---

## 1. 通用约定

- **Base URL**：`/api/v1`（另有根级 `/health`、`/docs`、`/uploads/*`）。
- **认证**：请求头 `Authorization: Bearer <access_token>`（公开接口除外）。
- **响应包装**：`{ code, message, data }`；分页 `data` 为 `{ items, total, page, page_size }`。
- **字段风格**：请求与响应均为 `snake_case`；前端在 `http.ts` 边界转 camelCase。
- **上传**：`POST /upload/image` 用 `multipart/form-data`，字段名 `file`。

分页参数（凡标注「分页」的列表）：`page`（默认 1，≥1）、`page_size`（默认 20，1–50）。

## 2. 认证 /auth

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/auth/register/verify` | 公开 | 校验注册码 |
| POST | `/auth/register` | 公开 | 注册（成功即登录返回双 token） |
| POST | `/auth/login` | 公开 | 登录（昵称或 ID） |
| POST | `/auth/refresh` | 公开 | 刷新双 token |
| POST | `/auth/recover` | 公开 | 找回密码 |
| POST | `/auth/logout` | 登录 | 登出（无状态，前端清本地） |

**请求体字段：**

| 端点 | 字段 | 类型 | 约束 |
|------|------|------|------|
| register/verify | `registration_key` | string | 4–32 |
| register | `registration_key` | string | 4–32 |
| | `nickname` | string | 2–20（唯一） |
| | `password` | string | 6–64 |
| | `avatar` | string? | 可选 |
| login | `account` | string | 1–20（昵称或 ID） |
| | `password` | string | 6–64 |
| refresh | `refresh_token` | string | — |
| recover | `account` | string | 1–20 |
| | `recovery_key` | string | 4–32 |
| | `new_password` | string | 6–64 |

**login / register / refresh 返回 data（AuthTokens）：**

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "user": { "id": 1, "nickname": "reader", "avatar": "...", "role": "user",
            "exp": 860, "level": 8, "title": "万卷书生",
            "exp_in_level": 60, "exp_to_next": 40 }
}
```

**register/verify 返回 data：** `{ "valid": true }`；recover/logout 返回 `data: null`。

## 3. 用户 /users

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/users/me` | 登录 | 当前用户信息 |
| PATCH | `/users/me` | 登录 | 改昵称/头像（部分更新） |
| POST | `/users/me/password` | 登录 | 修改密码 |

**PATCH /users/me 请求体：** `nickname`（string?, 2–20）、`avatar`（string?）。仅提交变更字段；昵称未改不触发唯一性校验。

**返回 data（UserOut）**：同 `login` 的 `user` 结构。

**POST /users/me/password 请求体：** `old_password`（6–64）、`new_password`（6–64）。

## 4. 书籍 /books

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/books/categories` | 公开 | 分类列表 |
| GET | `/books` | 公开 | 广场列表（分页） |
| GET | `/books/{book_id}` | 公开（可选登录） | 详情（含目录/进度/书架状态） |
| GET | `/books/{book_id}/update-logs` | 公开 | 更新日志 |
| GET | `/books/{book_id}/comments` | 公开 | 书评列表（树） |
| POST | `/books/{book_id}/comments` | 登录 | 发表书评 |

**GET /books 查询参数：** `category`（可选，`全部` 视为不过滤）、`keyword`（书名/作者模糊）、`sort`（`updated` 默认 / `words`）、`page`、`page_size`。

**GET /books/{id} 返回 data：**

```json
{
  "id": 1, "title": "雨夜列车", "author": "林暮", "author_id": 7,
  "category": "悬疑", "description": "...", "cover": "...",
  "word_count": 4800, "updated_at": "2026-06-20",
  "chapters": [{ "id": 1, "title": "第一节 候车室", "word_count": 1600 }],
  "progress": { "chapter_id": 2, "offset": 0.38 },
  "in_shelf": true
}
```

**POST /books/{id}/comments 请求体：** `content`（1–500）、`parent_id`（int?, ≥1，一级回复）。

## 5. 章节 /chapters

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/chapters/{chapter_id}` | 公开 | 章节正文（含 blocks/paragraphs） |

**返回 data（ChapterOut）：**

```json
{
  "id": 1, "book_id": 1, "title": "第一节 候车室",
  "content": "正文……",
  "paragraphs": ["段1", "段2"],
  "blocks": [
    { "type": "text", "text": "段1", "paragraph_index": 0 },
    { "type": "image", "url": "/uploads/abc.png", "after_paragraph_index": 1 },
    { "type": "text", "text": "段2", "paragraph_index": 1 }
  ],
  "word_count": 1600
}
```

说明：`blocks` 中图片块不占用 `paragraph_index`；`paragraphs` 为兼容字段（仅文本段）。

## 6. 评论 /comments

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/comments/paragraph/by-chapter/{chapter_id}` | 公开 | 整章段评汇总 |
| GET | `/comments/paragraph` | 公开 | 单段段评列表 |
| POST | `/comments/paragraph` | 登录 | 发表段评 |
| GET | `/comments/chapter/{chapter_id}` | 公开 | 章评列表 |
| POST | `/comments/chapter` | 登录 | 发表章评 |
| DELETE | `/comments/{comment_id}` | 本人/作者/管理员 | 删除评论 |
| POST | `/comments/{comment_id}/pin` | 作者/管理员 | 置顶评论 |

**GET /comments/paragraph 查询参数：** `chapter_id`、`paragraph_index`（≥0）。

**GET by-chapter 返回 data：** `Record<paragraph_index, CommentItem[]>`（段评按段分组）。

**POST /comments/paragraph 请求体：** `chapter_id`、`paragraph_index`（≥0）、`content`（1–500）、`parent_id`（int?, ≥1）。

**POST /comments/chapter 请求体：** `chapter_id`、`content`（1–500）、`parent_id`（int?）。

**DELETE /comments/{id} 与 POST /comments/{id}/pin 查询参数：** `type`（必填，`paragraph` / `chapter` / `book`）。

**评论项（CommentOut）：**

```json
{
  "id": 1, "user": "晚风读者", "user_id": 4,
  "avatar": "...", "level": 10, "title": "欲阅宗师",
  "content": "...", "is_pinned": false, "parent_id": null,
  "replies": []
}
```

## 7. 书架 /bookshelf

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/bookshelf` | 登录 | 我的书架（按最近阅读排序） |
| POST | `/bookshelf` | 登录 | 加入书架 |
| DELETE | `/bookshelf/{book_id}` | 登录 | 移出书架 |

**POST 请求体：** `book_id`（int）。

**GET 返回 data（BookshelfItemOut）：**

```json
{
  "id": 1, "title": "雨夜列车", "author": "林暮", "cover": "...",
  "word_count": 4800, "updated_at": "2026-06-20",
  "progress": 38, "chapter_id": 2, "chapter_title": "第二节 空座",
  "read_at": "2026-07-03 10:00"
}
```

## 8. 阅读 /reading

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/reading/progress/{book_id}` | 登录 | 获取进度 |
| PUT | `/reading/progress` | 登录 | 更新进度 |
| GET | `/reading/history` | 登录 | 阅读历史（分页） |

**PUT /reading/progress 请求体：** `book_id`、`chapter_id`、`offset`（float, 0–1）。

**返回 data（ReadingProgressOut）：** `{ "chapter_id": 2, "offset": 0.38 }`（无进度时 data 为 null）。

**GET /reading/history 参数：** `page`、`page_size`。返回 `PageResult<ReadingHistoryOut>`：

```json
{ "id": 1, "book_id": 1, "chapter_id": 2, "title": "雨夜列车",
  "cover": "...", "chapter_title": "第二节 空座", "read_at": "2026-07-03 10:00" }
```

## 9. 个人 /profile

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/profile/check-in` | 登录 | 签到 |
| GET | `/profile/check-in/status` | 登录 | 今日签到状态 |
| GET | `/profile/exp-logs` | 登录 | 经验流水（分页） |
| GET | `/profile/titles` | 登录 | 全部头衔与当前进度 |
| POST | `/profile/author-application` | 登录 | 提交作者申请 |
| GET | `/profile/author-application` | 登录 | 申请状态 |
| GET | `/profile/reader-settings` | 登录 | 阅读设置 |
| PUT | `/profile/reader-settings` | 登录 | 保存阅读设置 |

**POST /profile/check-in 返回 data（CheckInOut）：**

```json
{
  "fortune_text": "今日宜读书，忌熬夜。", "exp_gained": 12, "exp": 892,
  "leveled_up": false, "new_title": null, "level": 8, "title": "万卷书生"
}
```

**GET /profile/check-in/status 返回 data：** `{ "checked_in": true, "fortune_text": "..." }`。

**GET /profile/exp-logs 返回 data：** `PageResult<ExpLogOut>`（`source` 已映射为中文：每日签到/阅读/评论）。

**GET /profile/titles 返回 data（TitlesOut）：**

```json
{
  "level": 8, "title": "万卷书生", "exp": 892,
  "exp_in_level": 292, "exp_to_next": 8, "progress": 0.973,
  "tiers": [{ "level": 1, "title": "门外读者", "min_exp": 0, "unlocked": true, "current": false }]
}
```

**POST /profile/author-application 请求体：** `reason`（10–500 字）。已有待审核申请返回 `409`。

**GET /profile/author-application 返回 data：** `{ "status": "pending", "reason": "...", "review_note": null }`（无申请为 null）。

**reader-settings：** GET 返回 `{ "settings": {...} | null }`；PUT 请求体 `{ "settings": {...} }`（JSON 原样存取）。

## 10. 作者 /author

全部需要作者权限（author/admin/superadmin）。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/author/books` | 我的作品 |
| POST | `/author/books` | 新建作品 |
| PATCH | `/author/books/{book_id}` | 编辑作品 |
| POST | `/author/books/{book_id}/publish` | 发布 |
| POST | `/author/books/{book_id}/unpublish` | 下架 |
| DELETE | `/author/books/{book_id}` | 删除（仅草稿） |
| GET | `/author/books/{book_id}/chapters` | 章节列表 |
| POST | `/author/books/{book_id}/chapters` | 新增章节 |
| GET | `/author/chapters/{chapter_id}` | 章节详情（含正文） |
| PATCH | `/author/chapters/{chapter_id}` | 编辑章节 |
| DELETE | `/author/chapters/{chapter_id}` | 删除章节 |
| PUT | `/author/books/{book_id}/chapters/reorder` | 章节排序 |

**请求体字段：**

| 端点 | 字段 |
|------|------|
| POST /author/books | `title`（1–100）、`description`（≤2000, 默认 ""）、`category`（≤50, 默认 "其他"）、`cover`（string?） |
| PATCH /author/books/{id} | 同上，均可选（部分更新） |
| POST /author/books/{id}/chapters | `title`（1–100）、`content`（≤50000, 默认 ""） |
| PATCH /author/chapters/{id} | `title`、`content`（均可选） |
| PUT reorder | `chapter_ids`（int[]，须包含全部章节 id） |

**作品（AuthorBookOut）：**

```json
{
  "id": 1, "title": "雨夜列车", "description": "...", "cover": "...",
  "category": "悬疑", "status": "published", "admin_delisted": false,
  "word_count": 4800, "chapter_count": 3, "updated_at": "2026-06-20"
}
```

**章节（AuthorChapterOut）：** `{ id, title, word_count, sort_order, updated_at }`；章节详情加 `content`。

## 11. 上传 /upload

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/upload/image` | 登录 | 图片上传（multipart，字段 `file`） |

限制：MIME ∈ {jpeg, png, webp, gif}（content-type + 魔数双校验）；≤ `MAX_UPLOAD_MB`（默认 2MB）。

**返回 data：** `{ "url": "/uploads/<uuid>.png" }`（相对路径，前端展示时拼 origin）。

## 12. 管理 /admin

全部需要管理员权限（admin/superadmin）；标注「超管」的仅 superadmin。

### 12.1 用户 `/admin/users`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/admin/users` | admin | 用户列表（分页，`keyword` 可选） |
| PATCH | `/admin/users/{user_id}/status` | admin | 封禁/解封（`status`: active/banned） |
| PATCH | `/admin/users/{user_id}/role` | 超管 | 改角色 |

规则：不能封禁自己；普通管理员不能改管理员账号；授予/修改管理员角色仅超管。

### 12.2 密钥 `/admin/keys`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/admin/keys/registration` | admin | 批量生成注册码 |
| GET | `/admin/keys/registration` | admin | 注册码列表（分页） |
| POST | `/admin/keys/recovery` | admin | 生成找回密钥 |

- 生成注册码请求体：`count`（1–50）、`expire_days`（int?, 1–365）。
- 找回密钥请求体：`user_id`（≥1）。返回 `{ code, user_id, nickname }`（默认 7 天有效，作废该用户旧未用密钥）。
- 注册码项：`{ id, code, status, used_by, created_at, expires_at }`。

### 12.3 书籍 `/admin/books`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/admin/books` | admin | 全站书籍（分页） |
| PATCH | `/admin/books/{book_id}/status` | admin | 上架/下架（`status`: published/unpublished；下架置 `admin_delisted`） |
| DELETE | `/admin/books/{book_id}` | admin | 强制删除（级联清理） |

### 12.4 章节 `/admin/chapters`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/admin/chapters/by-book/{book_id}` | admin | 书籍章节列表 |
| GET | `/admin/chapters/{chapter_id}` | admin | 章节详情（含正文） |
| PATCH | `/admin/chapters/{chapter_id}` | admin | 编辑章节（`title`/`content` 可选） |

### 12.5 申请 `/admin/applications`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/admin/applications` | admin | 申请列表（分页，`status` 可选） |
| PATCH | `/admin/applications/{app_id}` | admin | 审核（`status`: approved/rejected；`review_note` 可选） |

审核通过且用户当前为 user 时角色升级为 author；重复处理返回 `409`。

### 12.6 评论 `/admin/comments`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/admin/comments` | admin | 评论列表 |
| POST | `/admin/comments/{comment_id}/hide` | admin | 隐藏 |
| POST | `/admin/comments/{comment_id}/unhide` | admin | 恢复显示 |

**GET 查询参数：** `type`（默认 chapter；paragraph/chapter/book）、`keyword`（可选）、`visibility`（默认 visible；visible/hidden/all）、`page`、`page_size`。

**hide/unhide 查询参数：** `type`（必填）。

**评论项（AdminCommentOut）：**

```json
{
  "id": 1, "type": "chapter", "user": "晚风读者", "user_id": 4,
  "avatar": "...", "content": "...", "book_title": "雨夜列车", "book_id": 1,
  "chapter_title": "第一节 候车室", "paragraph_index": null,
  "is_hidden": false, "created_at": "2026-07-03 10:00"
}
```

## 13. 其他端点

| 路径 | 说明 |
|------|------|
| `GET /health` | 健康检查，裸返回 `{"status": "ok"}`（不走 ApiResponse） |
| `GET /docs`、`/redoc` | OpenAPI 文档（生产关闭） |
| `/uploads/*` | 静态文件（头像、封面、章节插图） |
| `/{spa_path:path}` | 生产 SPA 回退（`api/`、`uploads/` 前缀 404） |

## 14. 鉴权依赖与分页

`app/api/deps.py` 提供的依赖：

| 依赖 | 行为 |
|------|------|
| `get_current_user` | 无/无效 Token → `401`；封禁 → `40301` |
| `get_current_user_optional` | 匿名放行（公开读接口） |
| `require_author` | 非 author/admin/superadmin → `40302` |
| `require_admin` | 非 admin/superadmin → `40303` |
| `require_superadmin` | 非 superadmin → `40303` |
| `get_pagination` / `Pagination` | `page≥1`、`1≤page_size≤50`，非法 → `400` |

> 说明：`/reading/history` 与 `/profile/exp-logs` 使用原生 `page`/`page_size` 查询参数（Service 层静默钳制），不走 `Pagination` 依赖；评论删除/置顶与后台隐藏/恢复必须携带 `type` 查询参数。

---

*文档结束 · 欲阅 08-API 接口文档 v1.0*
