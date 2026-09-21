import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiResponse } from '@/types/api'
import { ErrorCode } from '@/types/enums'
import { keysToCamel, keysToSnake } from '@/utils/caseTransform'
import { AppError } from '@/utils/appError'
import { DEFAULT_ERROR_MESSAGES } from '@/utils/errorHandler'
import { clearToken, getRefreshToken, getToken, setTokens } from '@/utils/token'
import { invalidateSession } from '@/utils/session'
import { useUserStore } from '@/stores/user'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
})

/** 是否正在刷新 Token，避免并发重复刷新 */
let isRefreshing = false
/** 刷新期间挂起的请求 */
let refreshQueue: Array<(token: string | null) => void> = []

function flushRefreshQueue(token: string | null) {
  refreshQueue.forEach((cb) => cb(token))
  refreshQueue = []
}

function toAppErrorFromBody(body: ApiResponse, httpStatus: number): AppError {
  const code = body.code ?? ErrorCode.INTERNAL_ERROR
  const message = body.message || DEFAULT_ERROR_MESSAGES[code] || '操作失败'
  return new AppError(code, message, { httpStatus, data: body.data })
}

function toAppErrorFromAxios(error: AxiosError<ApiResponse>): AppError {
  if (error.code === 'ECONNABORTED') {
    return new AppError(ErrorCode.NETWORK_ERROR, '请求超时，请稍后重试', { httpStatus: null, cause: error })
  }
  if (!error.response) {
    return new AppError(ErrorCode.NETWORK_ERROR, DEFAULT_ERROR_MESSAGES[ErrorCode.NETWORK_ERROR], {
      httpStatus: null,
      cause: error,
    })
  }

  const body = error.response.data
  if (body && typeof body === 'object' && 'code' in body) {
    return toAppErrorFromBody(body as ApiResponse, error.response.status)
  }

  const status = error.response.status
  const codeMap: Record<number, number> = {
    400: ErrorCode.BAD_REQUEST,
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    409: ErrorCode.CONFLICT,
    500: ErrorCode.INTERNAL_ERROR,
  }
  const code = codeMap[status] ?? ErrorCode.INTERNAL_ERROR
  return new AppError(code, DEFAULT_ERROR_MESSAGES[code] ?? '请求失败', {
    httpStatus: status,
    cause: error,
  })
}

async function tryRefreshToken(): Promise<string | null> {
  const refresh = getRefreshToken()
  if (!refresh) return null
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
  try {
    const { data } = await axios.post<ApiResponse<{ accessToken: string; refreshToken: string }>>(
      `${baseURL}/auth/refresh`,
      keysToSnake({ refreshToken: refresh }),
    )
    const body = keysToCamel(data) as ApiResponse<{
      accessToken: string
      refreshToken: string
    }>
    if (body.code !== ErrorCode.OK || !body.data?.accessToken) {
      return null
    }
    setTokens(body.data.accessToken, body.data.refreshToken)
    useUserStore().$patch({ token: body.data.accessToken })
    return body.data.accessToken
  } catch {
    return null
  }
}

/** 请求：业务 camelCase → 传输 snake_case */
http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (config.data && typeof config.data === 'object') {
    config.data = keysToSnake(config.data)
  }
  if (config.params && typeof config.params === 'object') {
    config.params = keysToSnake(config.params)
  }
  return config
})

/** 响应：snake_case → camelCase；code !== 0 视为业务失败 */
http.interceptors.response.use(
  (response) => {
    let body = response.data as ApiResponse
    if (body && typeof body === 'object' && 'data' in body) {
      body = keysToCamel(body) as ApiResponse
      response.data = body
    } else {
      response.data = keysToCamel(response.data)
    }

    const normalized = response.data as ApiResponse
    if (normalized && typeof normalized.code === 'number' && normalized.code !== ErrorCode.OK) {
      return Promise.reject(toAppErrorFromBody(normalized, response.status))
    }

    return response
  },
  async (error: AxiosError<ApiResponse>) => {
    const originalConfig = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    let appError = toAppErrorFromAxios(error)

    if (appError.isTokenExpired && originalConfig && !originalConfig._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push((token) => {
            if (!token) {
              reject(appError)
              return
            }
            originalConfig.headers.Authorization = `Bearer ${token}`
            resolve(http(originalConfig))
          })
        })
      }

      originalConfig._retry = true
      isRefreshing = true
      try {
        const newToken = await tryRefreshToken()
        flushRefreshQueue(newToken)
        if (!newToken) {
          invalidateSession()
          return Promise.reject(appError)
        }
        originalConfig.headers.Authorization = `Bearer ${newToken}`
        return http(originalConfig)
      } catch (refreshError) {
        flushRefreshQueue(null)
        invalidateSession()
        return Promise.reject(normalizeRefreshError(refreshError, appError))
      } finally {
        isRefreshing = false
      }
    }

    if (error.response?.data) {
      error.response.data = keysToCamel(error.response.data) as ApiResponse
      appError = toAppErrorFromAxios(error)
    }

    return Promise.reject(appError)
  },
)

function normalizeRefreshError(refreshError: unknown, fallback: AppError): AppError {
  if (refreshError instanceof AppError) {
    return refreshError
  }
  return fallback
}

export { ErrorCode }
export default http
