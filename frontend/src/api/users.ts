import { request } from '@/api/request'
import type { UserInfo } from '@/types/user'

export function fetchCurrentUser() {
  return request<UserInfo>({ method: 'GET', url: '/users/me' })
}

export function updateProfile(data: { nickname?: string; avatar?: string }) {
  return request<UserInfo>({ method: 'PATCH', url: '/users/me', data })
}

export function changePassword(oldPassword: string, newPassword: string) {
  return request<null>({
    method: 'POST',
    url: '/users/me/password',
    data: { oldPassword, newPassword },
  })
}
