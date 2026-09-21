export interface CommentItem {
  id: number
  user: string
  userId: number
  avatar?: string
  level?: number
  title?: string
  content: string
  isPinned?: boolean
  parentId?: number | null
  replies?: CommentItem[]
}
