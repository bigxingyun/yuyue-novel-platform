<template>
  <div v-if="book" class="book-detail">
    <div class="book-main">
      <div class="book-hero">
        <div class="book-cover-wrap">
          <img :src="book.cover" :alt="book.title" class="book-cover" />
        </div>
        <div class="book-info">
          <span class="tag">{{ book.category }}</span>
          <h1 class="book-title">{{ book.title }}</h1>
          <p class="book-author">{{ book.author }}</p>
          <div class="book-stats">
            <span>{{ formatWords(book.wordCount) }}</span>
            <span>{{ book.chapters.length }} 章</span>
            <span>{{ book.updatedAt }} 更新</span>
          </div>
          <div class="book-actions">
            <button class="btn btn-primary" @click="startRead">
              <PhBookOpen :size="18" />
              {{ book.progress ? '继续阅读' : '开始阅读' }}
            </button>
            <button class="btn btn-secondary" @click="toggleShelf">
              <PhBookmarkSimple :size="18" :weight="inShelf ? 'fill' : 'regular'" />
              {{ inShelf ? '已在书架' : '加入书架' }}
            </button>
          </div>
        </div>
      </div>

      <section class="book-section">
        <h2 class="block-title">简介</h2>
        <p class="book-desc" :class="{ collapsed: !descExpanded }">{{ book.description }}</p>
        <button
          v-if="book.description.length > 80"
          class="expand-btn"
          @click="descExpanded = !descExpanded"
        >
          {{ descExpanded ? '收起' : '展开全部' }}
        </button>
      </section>

      <section class="book-section">
        <h2 class="block-title">更新日志</h2>
        <ul class="update-log">
          <li
            v-for="log in updateLogs"
            :key="log.chapterId"
            class="update-item"
            @click="goChapter(log.chapterId)"
          >
            <span class="update-date">{{ log.date }}</span>
            <span class="update-chapter">{{ log.chapterTitle }}</span>
            <span class="update-words">+{{ log.addedWords }} 字</span>
          </li>
        </ul>
      </section>
    </div>

    <CommentDock class="book-comments" title="书评" :count="comments.length" side>
      <template #list>
        <div v-if="comments.length" class="comment-list">
          <CommentItem
            v-for="c in comments"
            :key="c.id"
            :comment="c"
            type="book"
            :can-pin="canPinComments"
            :replying-to="replyingTo"
            @reply="replyingTo = $event"
            @pin="pinCommentItem"
            @delete="removeComment"
            @submit-reply="onSubmitReply"
            @cancel-reply="replyingTo = null"
          />
        </div>
        <p v-else class="comment-empty">暂无书评，写下第一条吧</p>
      </template>
      <template #compose>
        <textarea
          v-model="newComment"
          class="comment-input field-input"
          placeholder="写下你的感受…"
          rows="3"
        />
        <button class="btn btn-primary btn-sm btn-block" @click="postComment">发表书评</button>
      </template>
    </CommentDock>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PhBookOpen, PhBookmarkSimple } from '@phosphor-icons/vue'
import CommentDock from '@/components/comment/CommentDock.vue'
import CommentItem from '@/components/comment/CommentItem.vue'
import { fetchBookDetail, fetchUpdateLogs } from '@/api/books'
import { addToBookshelf, removeFromBookshelf } from '@/api/bookshelf'
import { useBookComments } from '@/composables/useBookComments'
import { useUserStore } from '@/stores/user'
import type { BookDetail, UpdateLog } from '@/types/book'
import type { CommentItem as CommentItemType } from '@/types/comment'
import { handleError, notify } from '@/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const book = ref<BookDetail | null>(null)
const updateLogs = ref<UpdateLog[]>([])
const inShelf = ref(false)
const descExpanded = ref(false)
const newComment = ref('')

const bookId = computed(() => Number(route.params.bookId))
const {
  comments,
  replyingTo,
  loadComments,
  submitComment,
  removeComment,
  pinCommentItem,
} = useBookComments(() => bookId.value)

const canPinComments = computed(
  () => !!userStore.userInfo && book.value?.authorId === userStore.userInfo.id,
)

function formatWords(n: number) {
  return n >= 10000 ? `${(n / 10000).toFixed(1)} 万字` : `${n} 字`
}

async function loadBook() {
  const id = bookId.value
  try {
    const [detail, logs] = await Promise.all([
      fetchBookDetail(id),
      fetchUpdateLogs(id),
    ])
    book.value = detail
    updateLogs.value = logs
    inShelf.value = detail.inShelf
    await loadComments()
  } catch (e) {
    handleError(e)
  }
}

onMounted(loadBook)

function startRead() {
  if (!book.value) return
  const chapterId = book.value.progress?.chapterId ?? book.value.chapters[0]?.id
  if (chapterId) router.push(`/read/${book.value.id}/${chapterId}`)
}

function goChapter(chapterId: number) {
  router.push(`/read/${book.value?.id}/${chapterId}`)
}

async function toggleShelf() {
  if (!book.value) return
  try {
    if (inShelf.value) {
      await removeFromBookshelf(book.value.id)
      inShelf.value = false
      notify('已从书架移除', 'success')
    } else {
      await addToBookshelf(book.value.id)
      inShelf.value = true
      notify('已加入书架', 'success')
    }
  } catch (e) {
    handleError(e)
  }
}

async function postComment() {
  if (!book.value || !newComment.value.trim()) return
  try {
    await submitComment(newComment.value)
    newComment.value = ''
  } catch (e) {
    handleError(e)
  }
}

async function onSubmitReply(parent: CommentItemType, text: string) {
  try {
    await submitComment(text, parent.id)
  } catch (e) {
    handleError(e)
  }
}
</script>

<style scoped>
.book-detail {
  display: flex;
  flex-direction: column;
  gap: 0;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 24px 20px 24px;
  min-height: calc(100dvh - var(--header-height));
}

@media (min-width: 900px) {
  .book-detail {
    display: grid;
    grid-template-columns: 1fr min(380px, 36%);
    gap: 28px;
    align-items: start;
    padding: 32px 28px 32px;
  }
}

.book-main {
  min-width: 0;
}

.book-hero {
  display: grid;
  gap: var(--space-6);
  margin-bottom: var(--space-8);
  padding: var(--space-5);
  border-radius: var(--radius-xl);
  background: linear-gradient(135deg, var(--color-surface), var(--color-bg-elevated));
  border: 1px solid var(--color-border-soft);
  box-shadow: var(--shadow-sm);
}

@media (min-width: 768px) {
  .book-hero {
    grid-template-columns: 220px 1fr;
    gap: 40px;
  }
}

.book-cover-wrap {
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  aspect-ratio: 5/7;
  max-width: 220px;
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-title {
  font-family: var(--font-serif);
  font-size: clamp(1.6rem, 4vw, 2.2rem);
  margin: 12px 0 8px;
}

.book-author {
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}

.book-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 24px;
}

.book-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.book-section {
  margin-bottom: 32px;
}

.block-title {
  font-family: var(--font-serif);
  font-size: 18px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border-soft);
}

.book-desc {
  font-size: 15px;
  line-height: 1.8;
  color: var(--color-text-secondary);
}

.book-desc.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.expand-btn {
  margin-top: 8px;
  font-size: 13px;
  color: var(--color-accent);
}

.update-log {
  display: flex;
  flex-direction: column;
}

.update-item {
  display: grid;
  grid-template-columns: 100px 1fr auto;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border-soft);
  cursor: pointer;
  font-size: 14px;
  transition: color var(--transition);
}

.update-item:hover {
  color: var(--color-accent);
}

.update-date,
.update-words {
  color: var(--color-text-muted);
  font-size: 13px;
}

.book-comments {
  height: min(52dvh, 520px);
}

@media (min-width: 900px) {
  .book-comments {
    position: sticky;
    top: calc(var(--header-height) + 16px);
    height: calc(100dvh - var(--header-height) - 48px);
  }
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-empty {
  text-align: center;
  font-size: 13px;
  color: var(--color-text-muted);
  padding: 24px 12px;
}

.comment-input {
  width: 100%;
  margin-bottom: 10px;
  resize: vertical;
  min-height: 72px;
}
</style>
