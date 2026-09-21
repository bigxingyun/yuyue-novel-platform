/** localStorage Token Key — 全项目唯一，禁止硬编码字符串 */
export const TOKEN_KEY = 'yuyue_access_token'
export const REFRESH_TOKEN_KEY = 'yuyue_refresh_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function setRefreshToken(token: string) {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

export function setTokens(accessToken: string, refreshToken: string) {
  setToken(accessToken)
  setRefreshToken(refreshToken)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}
