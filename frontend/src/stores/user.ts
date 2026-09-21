import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'
import { refreshToken as apiRefresh, logout as apiLogout } from '@/api/auth'
import { fetchCurrentUser } from '@/api/users'
import { ErrorCode } from '@/types/enums'
import { AppError } from '@/utils/appError'
import { getToken, getRefreshToken, setTokens } from '@/utils/token'
import { invalidateSession } from '@/utils/session'

function isAuthFailure(error: unknown): boolean {
  if (!(error instanceof AppError)) return false
  return (
    error.code === ErrorCode.UNAUTHORIZED ||
    error.code === ErrorCode.TOKEN_EXPIRED ||
    error.code === ErrorCode.ACCOUNT_BANNED
  )
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(getToken())
  const userInfo = ref<UserInfo | null>(null)
  const bootstrapped = ref(false)

  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)

  function setAuth(accessToken: string, refresh: string, user: UserInfo) {
    token.value = accessToken
    userInfo.value = user
    setTokens(accessToken, refresh)
    import('@/composables/useReaderSettingsSync').then(({ pullReaderSettingsFromCloud }) => {
      pullReaderSettingsFromCloud()
    })
  }

  async function logout() {
    try {
      if (token.value) await apiLogout()
    } catch {
      /* ignore */
    }
    invalidateSession()
    token.value = null
    userInfo.value = null
  }

  async function bootstrap() {
    if (!token.value && getRefreshToken()) {
      try {
        const result = await apiRefresh(getRefreshToken()!)
        setAuth(result.accessToken, result.refreshToken, result.user)
      } catch {
        invalidateSession()
        token.value = null
      }
    }

    if (!token.value) {
      bootstrapped.value = true
      return
    }

    try {
      userInfo.value = await fetchCurrentUser()
      const { pullReaderSettingsFromCloud } = await import('@/composables/useReaderSettingsSync')
      await pullReaderSettingsFromCloud()
    } catch (e) {
      if (isAuthFailure(e)) {
        invalidateSession()
        token.value = null
        userInfo.value = null
      }
    } finally {
      bootstrapped.value = true
    }
  }

  return { token, userInfo, isLoggedIn, bootstrapped, setAuth, logout, bootstrap }
})
