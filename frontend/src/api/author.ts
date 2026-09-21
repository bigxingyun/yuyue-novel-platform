import { request } from '@/api/request'

export interface AuthorBook {
  id: number
  title: string
  description: string
  cover: string
  category: string
  status: 'draft' | 'published' | 'unpublished'
  adminDelisted?: boolean
  wordCount: number
  chapterCount: number
  updatedAt: string
}

export function fetchAuthorBooks() {
  return request<AuthorBook[]>({ method: 'GET', url: '/author/books' })
}

export function createAuthorBook(data: {
  title: string
  description?: string
  category?: string
  cover?: string
}) {
  return request<AuthorBook>({ method: 'POST', url: '/author/books', data })
}

export function updateAuthorBook(
  bookId: number,
  data: { title?: string; description?: string; category?: string; cover?: string },
) {
  return request<AuthorBook>({ method: 'PATCH', url: `/author/books/${bookId}`, data })
}

export function publishAuthorBook(bookId: number) {
  return request<AuthorBook>({ method: 'POST', url: `/author/books/${bookId}/publish` })
}

export function unpublishAuthorBook(bookId: number) {
  return request<AuthorBook>({ method: 'POST', url: `/author/books/${bookId}/unpublish` })
}

export function deleteAuthorBook(bookId: number) {
  return request<null>({ method: 'DELETE', url: `/author/books/${bookId}` })
}

export interface AuthorChapter {
  id: number
  title: string
  wordCount: number
  sortOrder: number
  updatedAt: string
}

export function fetchAuthorChapters(bookId: number) {
  return request<AuthorChapter[]>({
    method: 'GET',
    url: `/author/books/${bookId}/chapters`,
  })
}

export function createAuthorChapter(
  bookId: number,
  data: { title: string; content?: string },
) {
  return request<AuthorChapter>({
    method: 'POST',
    url: `/author/books/${bookId}/chapters`,
    data,
  })
}

export function updateAuthorChapter(
  chapterId: number,
  data: { title?: string; content?: string },
) {
  return request<AuthorChapter>({
    method: 'PATCH',
    url: `/author/chapters/${chapterId}`,
    data,
  })
}

export function deleteAuthorChapter(chapterId: number) {
  return request<null>({ method: 'DELETE', url: `/author/chapters/${chapterId}` })
}

export function reorderAuthorChapters(bookId: number, chapterIds: number[]) {
  return request<AuthorChapter[]>({
    method: 'PUT',
    url: `/author/books/${bookId}/chapters/reorder`,
    data: { chapterIds },
  })
}

export function fetchAuthorChapterContent(chapterId: number) {
  return request<{ id: number; title: string; content: string; wordCount: number }>({
    method: 'GET',
    url: `/author/chapters/${chapterId}`,
  })
}
