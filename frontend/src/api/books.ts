import { request } from '@/api/request'
import type { PageResult } from '@/types/api'
import type {
  BookComment,
  BookDetail,
  BookListItem,
  ChapterDetail,
  UpdateLog,
} from '@/types/book'

export function fetchBookCategories() {
  return request<string[]>({ method: 'GET', url: '/books/categories' })
}

export function fetchBookList(params: {
  page?: number
  pageSize?: number
  category?: string
  keyword?: string
  sort?: 'updated' | 'words'
}) {
  const category = params.category === '全部' ? undefined : params.category
  return request<PageResult<BookListItem>>({
    method: 'GET',
    url: '/books',
    params: { ...params, category },
  })
}

export function fetchBookDetail(bookId: number) {
  return request<BookDetail>({
    method: 'GET',
    url: `/books/${bookId}`,
  })
}

export function fetchUpdateLogs(bookId: number) {
  return request<UpdateLog[]>({
    method: 'GET',
    url: `/books/${bookId}/update-logs`,
  })
}

export function fetchBookComments(bookId: number) {
  return request<BookComment[]>({
    method: 'GET',
    url: `/books/${bookId}/comments`,
  })
}

export function createBookComment(bookId: number, content: string) {
  return request<BookComment>({
    method: 'POST',
    url: `/books/${bookId}/comments`,
    data: { content },
  })
}

export function fetchChapter(chapterId: number) {
  return request<ChapterDetail>({
    method: 'GET',
    url: `/chapters/${chapterId}`,
  })
}
