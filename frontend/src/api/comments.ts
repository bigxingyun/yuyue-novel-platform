import { request } from '@/api/request'
import type { CommentItem } from '@/types/comment'

export function fetchParagraphCommentsByChapter(chapterId: number) {
  return request<Record<string, CommentItem[]>>({
    method: 'GET',
    url: `/comments/paragraph/by-chapter/${chapterId}`,
  })
}

export function fetchParagraphComments(chapterId: number, paragraphIndex: number) {
  return request<CommentItem[]>({
    method: 'GET',
    url: '/comments/paragraph',
    params: { chapterId, paragraphIndex },
  })
}

export function createParagraphComment(data: {
  chapterId: number
  paragraphIndex: number
  content: string
  parentId?: number
}) {
  return request<CommentItem>({
    method: 'POST',
    url: '/comments/paragraph',
    data,
  })
}

export function fetchChapterComments(chapterId: number) {
  return request<CommentItem[]>({
    method: 'GET',
    url: `/comments/chapter/${chapterId}`,
  })
}

export function createChapterComment(
  chapterId: number,
  content: string,
  parentId?: number,
) {
  return request<CommentItem>({
    method: 'POST',
    url: '/comments/chapter',
    data: { chapterId, content, parentId },
  })
}

export function deleteComment(commentId: number, type: 'paragraph' | 'chapter' | 'book') {
  return request<null>({
    method: 'DELETE',
    url: `/comments/${commentId}`,
    params: { type },
  })
}

export function pinComment(commentId: number, type: 'paragraph' | 'chapter' | 'book') {
  return request<CommentItem>({
    method: 'POST',
    url: `/comments/${commentId}/pin`,
    params: { type },
  })
}

export function fetchBookCommentsTree(bookId: number) {
  return request<CommentItem[]>({
    method: 'GET',
    url: `/books/${bookId}/comments`,
  })
}

export function createBookComment(bookId: number, content: string, parentId?: number) {
  return request<CommentItem>({
    method: 'POST',
    url: `/books/${bookId}/comments`,
    data: { content, parentId },
  })
}
