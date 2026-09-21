import { ref } from 'vue'
import type { AppError } from '@/utils/appError'
import { handleError, type HandleErrorOptions } from '@/utils/errorHandler'

/**
 * 封装异步 API 调用的标准错误处理模式
 *
 * @example
 * const { loading, run } = useApiAction()
 * await run(() => loginApi(form), { message: '登录失败' })
 */
export function useApiAction() {
  const loading = ref(false)
  const lastError = ref<AppError | null>(null)

  async function run<T>(
    fn: () => Promise<T>,
    options: HandleErrorOptions & { rethrow?: boolean } = {},
  ): Promise<T | null> {
    loading.value = true
    lastError.value = null
    try {
      return await fn()
    } catch (error) {
      lastError.value = handleError(error, options)
      if (options.rethrow) {
        throw lastError.value
      }
      return null
    } finally {
      loading.value = false
    }
  }

  return { loading, lastError, run }
}
