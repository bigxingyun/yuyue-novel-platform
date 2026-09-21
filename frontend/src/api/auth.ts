import { request } from '@/api/request'
import type { UserInfo } from '@/types/user'

export interface AuthResult {
  accessToken: string
  refreshToken: string
  user: UserInfo
}

export function login(account: string, password: string) {
  return request<AuthResult>({
    method: 'POST',
    url: '/auth/login',
    data: { account, password },
  })
}

export function refreshToken(refreshToken: string) {
  return request<AuthResult>({
    method: 'POST',
    url: '/auth/refresh',
    data: { refreshToken },
  })
}

export function verifyRegistrationKey(registrationKey: string) {
  return request<{ valid: boolean }>({
    method: 'POST',
    url: '/auth/register/verify',
    data: { registrationKey },
  })
}

export function register(data: {
  registrationKey: string
  nickname: string
  password: string
  avatar?: string
}) {
  return request<AuthResult>({
    method: 'POST',
    url: '/auth/register',
    data,
  })
}

export function recoverPassword(data: {
  account: string
  recoveryKey: string
  newPassword: string
}) {
  return request<null>({
    method: 'POST',
    url: '/auth/recover',
    data,
  })
}

export function logout() {
  return request<null>({ method: 'POST', url: '/auth/logout' })
}
