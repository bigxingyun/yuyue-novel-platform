import { ref } from 'vue'
import {
  createBookComment,
  deleteComment,
  fetchBookCommentsTree,
  pinComment,
} from '@/api/comments'
import type { CommentItem } from '@/types/comment'
import { handleError, notify } from '@/utils/errorHandler'

export function useBookComments(bookId: () => number) {
  const comments = ref<CommentItem[]>([])
  const replyingTo = ref<CommentItem | null>(null)

  async function loadComments() {
    comments.value = await fetchBookCommentsTree(bookId())
  }

  async function submitComment(text: string, parentId?: number) {
    if (!text.trim()) return
    await createBookComment(bookId(), text.trim(), parentId)
    replyingTo.value = null
    await loadComments()
    notify(parentId ? '回复已发表' : '书评已发表', 'success')
  }

  async function removeComment(comment: CommentItem) {
    if (!confirm('确定删除该评论？')) return
    try {
      await deleteComment(comment.id, 'book')
      await loadComments()
      notify('已删除', 'success')
    } catch (e) {
      handleError(e)
    }
  }

  async function pinCommentItem(comment: CommentItem) {
    try {
      await pinComment(comment.id, 'book')
      await loadComments()
      notify('已置顶', 'success')
    } catch (e) {
      handleError(e)
    }
  }

  return {
    comments,
    replyingTo,
    loadComments,
    submitComment,
    removeComment,
    pinCommentItem,
  }
}
