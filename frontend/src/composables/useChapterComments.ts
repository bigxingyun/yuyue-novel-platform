import { ref } from 'vue'
import {
  createChapterComment,
  createParagraphComment,
  deleteComment,
  fetchChapterComments,
  fetchParagraphCommentsByChapter,
  pinComment,
} from '@/api/comments'
import type { CommentItem } from '@/types/comment'
import { handleError, notify } from '@/utils/errorHandler'

export function useChapterComments(getChapterId: () => number | undefined) {
  const chapterCommentsByChapter = ref<Record<number, CommentItem[]>>({})
  const paraCommentsByChapter = ref<Record<number, Record<number, CommentItem[]>>>({})
  const replyingTo = ref<CommentItem | null>(null)
  let loadToken = 0

  function getChapterComments(chapterId: number): CommentItem[] {
    return chapterCommentsByChapter.value[chapterId] ?? []
  }

  function getParaComments(chapterId: number, paragraphIndex: number): CommentItem[] {
    return paraCommentsByChapter.value[chapterId]?.[paragraphIndex] ?? []
  }

  function paraCommentCount(chapterId: number, paragraphIndex: number): number {
    return getParaComments(chapterId, paragraphIndex).length
  }

  async function loadComments(chapterId: number) {
    const token = ++loadToken
    try {
      const [chComments, paraGroups] = await Promise.all([
        fetchChapterComments(chapterId),
        fetchParagraphCommentsByChapter(chapterId),
      ])
      if (token !== loadToken) return
      const mapped: Record<number, CommentItem[]> = {}
      Object.entries(paraGroups).forEach(([idx, list]) => {
        mapped[Number(idx)] = list
      })
      chapterCommentsByChapter.value = {
        ...chapterCommentsByChapter.value,
        [chapterId]: chComments,
      }
      paraCommentsByChapter.value = {
        ...paraCommentsByChapter.value,
        [chapterId]: mapped,
      }
    } catch (e) {
      handleError(e, { silent: true })
    }
  }

  async function prefetchComments(chapterId: number) {
    if (chapterCommentsByChapter.value[chapterId]) return
    try {
      await loadComments(chapterId)
    } catch {
      /* 预加载失败不影响阅读 */
    }
  }

  async function submitChapter(text: string, parentId?: number, chapterIdOverride?: number) {
    const chapterId = chapterIdOverride ?? getChapterId()
    if (!chapterId || !text.trim()) return
    await createChapterComment(chapterId, text.trim(), parentId)
    replyingTo.value = null
    await loadComments(chapterId)
    notify(parentId ? '回复已发表' : '章评已发表', 'success')
  }

  async function submitParagraph(index: number, text: string, parentId?: number) {
    const chapterId = getChapterId()
    if (!chapterId || !text.trim()) return
    await createParagraphComment({
      chapterId,
      paragraphIndex: index,
      content: text.trim(),
      parentId,
    })
    replyingTo.value = null
    await loadComments(chapterId)
    notify(parentId ? '回复已发表' : '段评已发表', 'success')
  }

  async function removeComment(comment: CommentItem, type: 'chapter' | 'paragraph') {
    if (!confirm('确定删除该评论？')) return
    try {
      await deleteComment(comment.id, type)
      const chapterId = getChapterId()
      if (chapterId) await loadComments(chapterId)
      notify('已删除', 'success')
    } catch (e) {
      handleError(e)
    }
  }

  async function pinCommentItem(comment: CommentItem, type: 'chapter' | 'paragraph') {
    try {
      await pinComment(comment.id, type)
      const chapterId = getChapterId()
      if (chapterId) await loadComments(chapterId)
      notify('已置顶', 'success')
    } catch (e) {
      handleError(e)
    }
  }

  return {
    chapterCommentsByChapter,
    paraCommentsByChapter,
    replyingTo,
    getChapterComments,
    getParaComments,
    paraCommentCount,
    loadComments,
    prefetchComments,
    submitChapter,
    submitParagraph,
    removeComment,
    pinCommentItem,
  }
}
