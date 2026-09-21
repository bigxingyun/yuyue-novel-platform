<template>
  <div class="shelf page-container">
    <header class="shelf-header">
      <h1 class="section-title">我的书架</h1>
      <p class="section-desc">点击封面直达阅读；长按封面可从书架移除</p>
    </header>

    <div v-if="shelfBooks.length" class="shelf-grid">
      <article
        v-for="book in shelfBooks"
        :key="book.id"
        class="shelf-item"
        @click="goRead(book)"
        @touchstart.passive="onPressStart(book.id)"
        @touchend="onPressEnd"
        @touchcancel="onPressEnd"
        @mousedown="onPressStart(book.id)"
        @mouseup="onPressEnd"
        @mouseleave="onPressEnd"
      >
        <div class="shelf-cover">
          <img :src="book.cover" :alt="book.title" />
          <div class="shelf-progress-bar">
            <div class="shelf-progress-fill" :style="{ width: `${book.progress}%` }" />
          </div>
        </div>
        <h3 class="shelf-title">{{ book.title }}</h3>
        <p class="shelf-meta">
          {{ book.chapterTitle ? `读到「${book.chapterTitle}」` : '尚未开始' }}
          · {{ book.progress }}%
          <span v-if="book.readAt"> · {{ book.readAt }}</span>
        </p>
        <button class="shelf-remove" @click.stop="remove(book.id)">
          <PhTrash :size="16" />
        </button>
      </article>
    </div>

    <EmptyState
      v-else
      :icon="PhBookmark"
      title="书架空空如也"
      description="去书籍广场挑一本心仪的作品吧"
    >
      <RouterLink to="/square" class="btn btn-primary">前往广场</RouterLink>
    </EmptyState>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { PhBookmark, PhTrash } from '@phosphor-icons/vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { fetchBookshelf, removeFromBookshelf, type BookshelfItem } from '@/api/bookshelf'
import { handleError, notify } from '@/utils/errorHandler'

const router = useRouter()
const shelfBooks = ref<BookshelfItem[]>([])
let pressTimer: ReturnType<typeof setTimeout> | null = null
let longPressTriggered = false
const LONG_PRESS_MS = 550

async function loadShelf() {
  try {
    shelfBooks.value = await fetchBookshelf()
  } catch (e) {
    handleError(e)
  }
}

onMounted(loadShelf)

function goRead(book: BookshelfItem) {
  if (longPressTriggered) {
    longPressTriggered = false
    return
  }
  const chapterId = book.chapterId ?? 1
  router.push(`/read/${book.id}/${chapterId}`)
}

function onPressStart(id: number) {
  onPressEnd()
  pressTimer = setTimeout(() => {
    longPressTriggered = true
    remove(id)
    pressTimer = null
  }, LONG_PRESS_MS)
}

function onPressEnd() {
  if (pressTimer) {
    clearTimeout(pressTimer)
    pressTimer = null
  }
}

async function remove(id: number) {
  if (!confirm('确定从书架移除该书籍？')) {
    longPressTriggered = false
    return
  }
  longPressTriggered = false
  try {
    await removeFromBookshelf(id)
    shelfBooks.value = shelfBooks.value.filter((b) => b.id !== id)
    notify('已从书架移除', 'success')
  } catch (e) {
    handleError(e)
  }
}
</script>

<style scoped>
.shelf-header {
  margin-bottom: 28px;
}

.shelf-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
}

@media (min-width: 768px) {
  .shelf-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
}

.shelf-item {
  position: relative;
  cursor: pointer;
}

.shelf-cover {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  aspect-ratio: 5/7;
  box-shadow: var(--shadow-md);
  margin-bottom: 10px;
}

.shelf-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.shelf-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(0, 0, 0, 0.2);
}

.shelf-progress-fill {
  height: 100%;
  background: var(--color-accent);
}

.shelf-title {
  font-family: var(--font-serif);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.shelf-meta {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.shelf-remove {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: rgba(20, 23, 30, 0.55);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition);
}

.shelf-item:hover .shelf-remove {
  opacity: 1;
}
</style>
