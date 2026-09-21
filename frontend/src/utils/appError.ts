/**
 * 统一业务错误类 — 由 http.ts 拦截器构造，业务层 catch 使用
 */
export class AppError extends Error {
  readonly code: number
  readonly httpStatus: number | null
  readonly data: unknown
  readonly cause?: unknown

  constructor(
    code: number,
    message: string,
    options: { httpStatus?: number | null; data?: unknown; cause?: unknown } = {},
  ) {
    super(message)
    this.cause = options.cause
    this.name = 'AppError'
    this.code = code
    this.httpStatus = options.httpStatus ?? null
    this.data = options.data ?? null
  }

  get isUnauthorized(): boolean {
    return this.code === 401 || this.code === 40101
  }

  get isTokenExpired(): boolean {
    return this.code === 40101
  }

  get isForbidden(): boolean {
    return this.code === 403 || this.code === 40301
  }

  get isNotFound(): boolean {
    return this.code === 404 || (this.code >= 40401 && this.code < 40500)
  }

  get isValidation(): boolean {
    return this.code === 400
  }

  get isNetwork(): boolean {
    return this.code === -1
  }
}

export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError
}
