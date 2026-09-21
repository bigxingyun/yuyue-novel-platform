# 贡献指南

开发前请先读 **[docs/CONVENTIONS.md](./docs/CONVENTIONS.md)**。

## 文档分工

| 文档 | 回答的问题 |
|------|------------|
| [欲阅需求分析.md](./欲阅需求分析.md) | 做什么：功能、页面、接口、表结构 |
| [docs/CONVENTIONS.md](./docs/CONVENTIONS.md) | 怎么写：命名、分层、异常、文档格式 |
| [README.md](./README.md) | 怎么跑：本地开发与部署 |

业务改动更新需求分析；规范改动更新 CONVENTIONS；接口或表结构变更时两者都要改。

## 三条约定

1. **命名**：DB / API 用 `snake_case`，前端业务用 `camelCase`，在 `http.ts` 转换。
2. **分层**：View → api → Service → DB；响应统一 `{ code, message, data }`。
3. **异常**：后端 Service 抛 `AppException`；前端用 `AppError` + `handleError()`，不要空 `catch`。

## 异常处理速查

| 层级 | 做法 |
|------|------|
| 后端 Service | `raise_app(ErrorCode.XXX)` |
| 前端 api | 走 `request()` / `http`，不自行解析 axios 错误体 |
| 前端 View | `useApiAction()` 或 `catch → handleError()` |
| 表单 | `handleError(error, { silent: true })` 绑定到字段 |

详见 CONVENTIONS §3.8。

## 提交前

对照 CONVENTIONS §5.1 变更检查清单。
