import type { CommentItem } from '@/types/comment'

export interface CommentItemProps {
  comment: CommentItem
  type: 'paragraph' | 'chapter' | 'book'
  /** 当前用户是否为该书作者（可置顶） */
  canPin?: boolean
  compact?: boolean
}

export type { CommentItem }
