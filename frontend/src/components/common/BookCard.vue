<template>
  <article class="book-card" @click="$emit('click')">
    <div class="book-card-cover">
      <img :src="book.cover" :alt="book.title" loading="lazy" />
      <span v-if="book.progress" class="book-card-progress">{{ book.progress }}%</span>
    </div>
    <div class="book-card-body">
      <span class="tag">{{ book.category }}</span>
      <h3 class="book-card-title">{{ book.title }}</h3>
      <p class="book-card-author">{{ book.author }}</p>
      <p v-if="book.description" class="book-card-desc">{{ book.description }}</p>
      <div class="book-card-meta">
        <span>{{ formatWordCount(book.wordCount) }}</span>
        <span>{{ book.updatedAt }} 更新</span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { BookListItem } from '@/types/book'

type BookCardData = BookListItem & { description?: string; progress?: number }

defineProps<{ book: BookCardData }>()
defineEmits<{ click: [] }>()

function formatWordCount(n: number) {
  return n >= 10000 ? `${(n / 10000).toFixed(1)} 万字` : `${n} 字`
}
</script>

<style scoped>
.book-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-surface);
  border: 1px solid color-mix(in srgb, var(--color-border) 75%, transparent);
  box-shadow: var(--shadow-sm);
  transition:
    transform var(--transition),
    box-shadow var(--transition),
    border-color var(--transition);
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-accent-muted);
}

.book-card:active {
  transform: translateY(-1px);
}

.book-card-cover {
  position: relative;
  aspect-ratio: 5 / 7;
  overflow: hidden;
  background: var(--color-border-soft);
}

.book-card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.book-card:hover .book-card-cover img {
  transform: scale(1.03);
}

.book-card-progress {
  position: absolute;
  bottom: 10px;
  right: 10px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: var(--radius-full);
  background: rgba(20, 23, 30, 0.72);
  color: #fff;
  backdrop-filter: blur(8px);
}

.book-card-body {
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.book-card-title {
  font-family: var(--font-serif);
  font-size: var(--text-lg);
  font-weight: 600;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-card-author {
  font-size: 13px;
  color: var(--color-text-muted);
}

.book-card-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 2px;
}

.book-card-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-muted);
}
</style>
