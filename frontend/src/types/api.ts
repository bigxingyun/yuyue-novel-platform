/**
 * 统一 API 响应与分页类型 — 数据流入口格式（前端）
 */

/** 后端统一响应；拦截器解包前结构 */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T | null
}

/** 分页列表 data 结构 */
export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface PageParams {
  page?: number
  pageSize?: number
}
