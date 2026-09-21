import { request } from '@/api/request'

export interface BookshelfItem {
  id: number
  title: string
  author: string
  cover: string
  wordCount: number
  updatedAt: string
  progress: number
  chapterId?: number | null
  chapterTitle?: string | null
  readAt?: string | null
}

export function fetchBookshelf() {
  return request<BookshelfItem[]>({ method: 'GET', url: '/bookshelf' })
}

export function addToBookshelf(bookId: number) {
  return request<null>({ method: 'POST', url: '/bookshelf', data: { bookId } })
}

export function removeFromBookshelf(bookId: number) {
  return request<null>({ method: 'DELETE', url: `/bookshelf/${bookId}` })
}
