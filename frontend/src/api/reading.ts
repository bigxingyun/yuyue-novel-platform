import { request } from '@/api/request'
import type { PageResult } from '@/types/api'
import type { ReadingProgress } from '@/types/book'

export interface ReadingHistoryItem {
  id: number
  bookId: number
  chapterId: number
  title: string
  cover: string
  chapterTitle: string
  readAt: string
}

export function fetchReadingProgress(bookId: number) {
  return request<ReadingProgress | null>({
    method: 'GET',
    url: `/reading/progress/${bookId}`,
  })
}

export function updateReadingProgress(data: {
  bookId: number
  chapterId: number
  offset: number
}) {
  return request<ReadingProgress>({
    method: 'PUT',
    url: '/reading/progress',
    data,
  })
}

export function fetchReadingHistory(page = 1, pageSize = 20) {
  return request<PageResult<ReadingHistoryItem>>({
    method: 'GET',
    url: '/reading/history',
    params: { page, pageSize },
  })
}
