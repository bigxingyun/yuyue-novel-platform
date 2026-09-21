import type { AxiosRequestConfig } from 'axios'
import type { ApiResponse } from '@/types/api'
import { AppError } from '@/utils/appError'
import http from '@/api/http'

/**
 * 类型安全的 API 请求封装
 * - 成功时返回 data（已 camelCase）
 * - 失败时抛出 AppError（由拦截器构造）
 */
export async function request<T>(config: AxiosRequestConfig): Promise<T> {
  try {
    const response = await http(config)
    const body = response.data as ApiResponse<T>
    return body.data as T
  } catch (error) {
    if (error instanceof AppError) {
      throw error
    }
    throw error
  }
}