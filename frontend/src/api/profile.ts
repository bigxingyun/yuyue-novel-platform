import { request } from '@/api/request'
import type { ReaderSettings } from '@/composables/useReaderSettings'
import type { PageResult } from '@/types/api'

export interface CheckInResult {
  fortuneText: string
  expGained: number
  exp: number
  leveledUp?: boolean
  newTitle?: string | null
  level?: number
  title?: string
}

export interface CheckInStatus {
  checkedIn: boolean
  fortuneText?: string | null
}

export interface ExpLogItem {
  id: number
  source: string
  amount: number
  time: string
}

export function checkIn() {
  return request<CheckInResult>({ method: 'POST', url: '/profile/check-in' })
}

export function fetchCheckInStatus() {
  return request<CheckInStatus>({ method: 'GET', url: '/profile/check-in/status' })
}

export function fetchExpLogs(page = 1, pageSize = 20) {
  return request<PageResult<ExpLogItem>>({
    method: 'GET',
    url: '/profile/exp-logs',
    params: { page, pageSize },
  })
}

export function submitAuthorApplication(reason: string) {
  return request<{ status: string }>({
    method: 'POST',
    url: '/profile/author-application',
    data: { reason },
  })
}

export interface AuthorApplicationStatus {
  status: string
  reason: string
  reviewNote?: string | null
}

export function fetchAuthorApplication() {
  return request<AuthorApplicationStatus | null>({
    method: 'GET',
    url: '/profile/author-application',
  })
}

export function fetchReaderSettings() {
  return request<{ settings: Record<string, unknown> | null }>({
    method: 'GET',
    url: '/profile/reader-settings',
  })
}

export function updateReaderSettings(settings: ReaderSettings) {
  return request<{ settings: Record<string, unknown> }>({
    method: 'PUT',
    url: '/profile/reader-settings',
    data: { settings: settings as unknown as Record<string, unknown> },
  })
}

export interface TitleTierItem {
  level: number
  title: string
  minExp: number
  unlocked: boolean
  current: boolean
}

export interface TitlesInfo {
  level: number
  title: string
  exp: number
  expInLevel: number
  expToNext: number
  progress: number
  tiers: TitleTierItem[]
}

export function fetchTitles() {
  return request<TitlesInfo>({ method: 'GET', url: '/profile/titles' })
}
