import { ErrorCode } from '@/types/enums'
import { AppError } from '@/utils/appError'

/** 错误码默认文案（与后端 DEFAULT_ERROR_MESSAGES 保持一致） */
export const DEFAULT_ERROR_MESSAGES: Record<number, string> = {
  [ErrorCode.BAD_REQUEST]: '请求参数错误',
  [ErrorCode.UNAUTHORIZED]: '未登录或登录已失效',
  [ErrorCode.FORBIDDEN]: '无权执行此操作',
  [ErrorCode.NOT_FOUND]: '资源不存在',
  [ErrorCode.CONFLICT]: '操作冲突',
  [ErrorCode.INTERNAL_ERROR]: '服务器繁忙，请稍后重试',
  [ErrorCode.REGISTRATION_KEY_INVALID]: '注册码无效或已使用',
  [ErrorCode.NICKNAME_TAKEN]: '昵称已被占用',
  [ErrorCode.TOKEN_EXPIRED]: '登录已过期，请重新登录',
  [ErrorCode.ACCOUNT_BANNED]: '账号已被封禁，请联系管理员',
  [ErrorCode.AUTHOR_REQUIRED]: '需要作者权限',
  [ErrorCode.ADMIN_REQUIRED]: '需要管理员权限',
  [ErrorCode.BOOK_NOT_FOUND]: '书籍不存在',
  [ErrorCode.CHAPTER_NOT_FOUND]: '章节不存在',
  [ErrorCode.ALREADY_CHECKED_IN]: '今日已签到',
  [ErrorCode.NETWORK_ERROR]: '网络连接失败，请检查网络',
}

export type NotifyType = 'error' | 'success' | 'warning'

type NotifyFn = (message: string, type?: NotifyType) => void

/** 全局通知函数，由 App.vue 挂载 UI 组件后注入 */
let notifyFn: NotifyFn = (message, type = 'error') => {
  if (import.meta.env.DEV) {
    console[type === 'error' ? 'error' : 'log']('[notify]', message)
  }
}

export function setNotify(fn: NotifyFn) {
  notifyFn = fn
}

export function notify(message: string, type: NotifyType = 'error') {
  notifyFn(message, type)
}

export function getErrorMessage(error: unknown, fallback = '操作失败'): string {
  if (error instanceof AppError) {
    return error.message || DEFAULT_ERROR_MESSAGES[error.code] || fallback
  }
  if (error instanceof Error) {
    return error.message || fallback
  }
  return fallback
}

export interface HandleErrorOptions {
  /** 不弹出 Toast */
  silent?: boolean
  /** 自定义文案，覆盖 error.message */
  message?: string
  /** 错误时回调 */
  onError?: (error: AppError) => void
}

/**
 * 统一错误处理入口（View / Composable 在 catch 中调用）
 */
export function handleError(error: unknown, options: HandleErrorOptions = {}): AppError {
  const appError = normalizeError(error)
  options.onError?.(appError)

  if (!options.silent) {
    notify(options.message ?? getErrorMessage(appError))
  }

  return appError
}

/** 将任意 thrown 值规范为 AppError */
export function normalizeError(error: unknown): AppError {
  if (error instanceof AppError) {
    return error
  }
  if (error instanceof Error) {
    return new AppError(ErrorCode.INTERNAL_ERROR, error.message || DEFAULT_ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR], {
      cause: error,
    })
  }
  return new AppError(ErrorCode.INTERNAL_ERROR, DEFAULT_ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR])
}
