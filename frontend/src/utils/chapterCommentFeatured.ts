import type { CommentItem } from '@/types/comment'

/** 章评预览：作者置顶 > 回复最多 > 最早 */
export function pickFeaturedChapterComment(
  comments: CommentItem[],
  authorId: number,
): CommentItem | null {
  const tops = comments.filter((c) => !c.parentId)
  if (!tops.length) return null

  const authorPinned = tops.find((c) => c.isPinned && c.userId === authorId)
  if (authorPinned) return authorPinned

  const maxReplies = Math.max(...tops.map((c) => c.replies?.length ?? 0))
  if (maxReplies > 0) {
    return [...tops]
      .filter((c) => (c.replies?.length ?? 0) === maxReplies)
      .sort((a, b) => a.id - b.id)[0]
  }

  return [...tops].sort((a, b) => a.id - b.id)[0]
}

export function replyCountOf(comment: CommentItem): number {
  return comment.replies?.length ?? 0
}
