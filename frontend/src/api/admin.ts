import { request } from '@/api/request'
import type { PageResult } from '@/types/api'

export interface AdminUser {
  id: number
  nickname: string
  role: string
  status: string
  exp: number
  createdAt: string
}

export interface RegistrationKey {
  id: number
  code: string
  status: string
  usedBy: number | null
  createdAt: string
  expiresAt?: string | null
}

export interface AdminBook {
  id: number
  title: string
  author: string
  category: string
  status: string
  wordCount: number
  updatedAt: string
}

export interface AuthorApplication {
  id: number
  userId: number
  nickname: string
  reason: string
  status: string
  createdAt: string
  reviewNote?: string | null
}

export function fetchAdminUsers(page = 1, pageSize = 20, keyword?: string) {
  return request<PageResult<AdminUser>>({
    method: 'GET',
    url: '/admin/users',
    params: { page, pageSize, keyword: keyword?.trim() || undefined },
  })
}

export function updateUserStatus(userId: number, status: 'active' | 'banned') {
  return request<AdminUser>({
    method: 'PATCH',
    url: `/admin/users/${userId}/status`,
    data: { status },
  })
}

export function updateUserRole(userId: number, role: string) {
  return request<AdminUser>({
    method: 'PATCH',
    url: `/admin/users/${userId}/role`,
    data: { role },
  })
}

export function generateRegistrationKeys(count: number, expireDays?: number | null) {
  return request<RegistrationKey[]>({
    method: 'POST',
    url: '/admin/keys/registration',
    data: { count, expireDays: expireDays ?? undefined },
  })
}

export function fetchRegistrationKeys(page = 1, pageSize = 20) {
  return request<PageResult<RegistrationKey>>({
    method: 'GET',
    url: '/admin/keys/registration',
    params: { page, pageSize },
  })
}

export function generateRecoveryKey(userId: number) {
  return request<{ code: string; userId: number; nickname: string }>({
    method: 'POST',
    url: '/admin/keys/recovery',
    data: { userId },
  })
}

export function fetchAdminBooks(page = 1, pageSize = 20) {
  return request<PageResult<AdminBook>>({
    method: 'GET',
    url: '/admin/books',
    params: { page, pageSize },
  })
}

export function updateAdminBookStatus(bookId: number, status: 'published' | 'unpublished') {
  return request<AdminBook>({
    method: 'PATCH',
    url: `/admin/books/${bookId}/status`,
    data: { status },
  })
}

export function deleteAdminBook(bookId: number) {
  return request<null>({ method: 'DELETE', url: `/admin/books/${bookId}` })
}

export function fetchAuthorApplications(page = 1, pageSize = 20, status?: string) {
  return request<PageResult<AuthorApplication>>({
    method: 'GET',
    url: '/admin/applications',
    params: { page, pageSize, status: status && status !== 'all' ? status : undefined },
  })
}

export function reviewAuthorApplication(
  appId: number,
  status: 'approved' | 'rejected',
  reviewNote?: string,
) {
  return request<AuthorApplication>({
    method: 'PATCH',
    url: `/admin/applications/${appId}`,
    data: { status, reviewNote },
  })
}

export interface AdminComment {
  id: number
  type: string
  user: string
  userId: number
  avatar?: string
  content: string
  bookTitle: string
  bookId: number
  chapterTitle?: string | null
  paragraphIndex?: number | null
  isHidden?: boolean
  createdAt: string
}

export function fetchAdminComments(
  type: 'chapter' | 'paragraph' | 'book',
  page = 1,
  options?: { pageSize?: number; keyword?: string; visibility?: 'visible' | 'hidden' | 'all' },
) {
  return request<PageResult<AdminComment>>({
    method: 'GET',
    url: '/admin/comments',
    params: {
      type,
      page,
      pageSize: options?.pageSize ?? 20,
      keyword: options?.keyword?.trim() || undefined,
      visibility: options?.visibility ?? 'visible',
    },
  })
}

export function hideAdminComment(commentId: number, type: string) {
  return request<null>({
    method: 'POST',
    url: `/admin/comments/${commentId}/hide`,
    params: { type },
  })
}

export function unhideAdminComment(commentId: number, type: string) {
  return request<null>({
    method: 'POST',
    url: `/admin/comments/${commentId}/unhide`,
    params: { type },
  })
}

export interface AdminChapter {
  id: number
  title: string
  wordCount: number
  sortOrder: number
  updatedAt: string
}

export interface AdminChapterDetail extends AdminChapter {
  bookId: number
  bookTitle: string
  content: string
}

export function fetchAdminChapters(bookId: number) {
  return request<AdminChapter[]>({
    method: 'GET',
    url: `/admin/chapters/by-book/${bookId}`,
  })
}

export function fetchAdminChapter(chapterId: number) {
  return request<AdminChapterDetail>({
    method: 'GET',
    url: `/admin/chapters/${chapterId}`,
  })
}

export function updateAdminChapter(
  chapterId: number,
  data: { title?: string; content?: string },
) {
  return request<AdminChapterDetail>({
    method: 'PATCH',
    url: `/admin/chapters/${chapterId}`,
    data,
  })
}
