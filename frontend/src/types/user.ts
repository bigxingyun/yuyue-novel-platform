import type { UserRole } from '@/types/enums'

export interface UserInfo {
  id: number
  nickname: string
  avatar: string | null
  role: UserRole
  exp: number
  level?: number
  title?: string
  expInLevel?: number
  expToNext?: number
}
