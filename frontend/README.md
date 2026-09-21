# 欲阅 · 前端

Vue 3 + TypeScript + Vite 单页应用。开发前阅读 [docs/CONVENTIONS.md](../docs/CONVENTIONS.md)。

## 分层

```
View → composable / store → api/*.ts → http.ts → 后端
```

- 枚举：`src/types/enums.ts`
- API 类型：`src/types/api.ts`
- Case 转换：`src/utils/caseTransform.ts`（仅 `http.ts` 调用）
- View 不直接 `axios`；错误走 `AppError` + `handleError()` / `useApiAction()`

## 启动

先启动后端（见 `backend/README.md`），再：

```bash
npm install
npm run dev
```

- 开发地址：http://localhost:5173
- `.env.development` 中 `VITE_DEMO_MODE=true` 且 `npm run dev` 时可跳过登录守卫（仅本地调试，生产构建无效）

## 目录

| 路径 | 职责 |
|------|------|
| `src/views/` | 页面（`*View.vue`） |
| `src/components/` | 通用与业务组件 |
| `src/layouts/` | Default / Auth / Admin 布局 |
| `src/api/` | 接口封装 |
| `src/stores/` | Pinia（`user`、`device`） |
| `src/composables/` | 阅读器、评论、设备检测等组合逻辑 |
| `src/types/` | TS 类型与枚举 |
| `src/utils/` | token、错误处理、case 转换 |
| `src/styles/` | 全局样式与变量 |

## 主要 composable

| 文件 | 用途 |
|------|------|
| `useReader.ts` | 阅读页状态、进度上报 |
| `useReaderSettings.ts` | 字号、主题、翻页模式（localStorage） |
| `useReaderSettingsSync.ts` | 阅读设置云端同步 |
| `useReaderPagination.ts` | 左右滑动翻页 |
| `useReaderScrollChain.ts` | 滚动模式连续读下一章 |
| `useChapterComments.ts` | 章评加载与发表 |
| `useBookComments.ts` | 书评 |
| `useScrollLock.ts` | 浮层打开时锁背景滚动 |
| `useDevice.ts` | UA 检测 |
| `useApiAction.ts` | 带 loading 的请求封装 |
