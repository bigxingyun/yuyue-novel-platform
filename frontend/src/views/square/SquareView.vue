<template>
  <div class="square page-container">
    <header class="square-header">
      <div>
        <h1 class="section-title">书籍广场</h1>
        <p class="section-desc">发现值得一读的短篇小说</p>
      </div>
      <div class="search-box">
        <PhMagnifyingGlass :size="18" class="search-icon" />
        <input
          v-model="keyword"
          class="search-input"
          type="search"
          placeholder="搜索书名或作者"
        />
      </div>
    </header>

    <div class="filters">
      <div class="filter-row">
        <button
          v-for="cat in categories"
          :key="cat"
          class="filter-chip"
          :class="{ active: activeCategory === cat }"
          @click="activeCategory = cat"
        >
          {{ cat }}
        </button>
      </div>
      <div class="filter-row sort-row">
        <span class="filter-row-label">排序</span>
        <button
          v-for="opt in sortOptions"
          :key="opt.value"
          class="filter-chip"
          :class="{ active: sortBy === opt.value }"
          @click="sortBy = opt.value"
        >
          <component :is="opt.icon" :size="14" />
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div v-if="books.length" class="book-grid">
      <BookCard
        v-for="book in books"
        :key="book.id"
        :book="book"
        @click="goBook(book.id)"
      />
    </div>

    <EmptyState
      v-else-if="!loading"
      :icon="PhBooks"
      title="暂无匹配书籍"
      description="试试调整筛选条件或搜索关键词"
    >
      <button class="btn btn-secondary" @click="resetFilters">清除筛选</button>
    </EmptyState>

    <div v-if="books.length && total > books.length" class="load-more">
      <button class="btn btn-secondary" :disabled="loading" @click="loadMore">
        {{ loading ? '加载中…' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { PhBooks, PhClock, PhMagnifyingGlass, PhTextAa } from '@phosphor-icons/vue'
import BookCard from '@/components/common/BookCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { fetchBookList, fetchBookCategories } from '@/api/books'
import type { BookListItem } from '@/types/book'
import { handleError } from '@/utils/errorHandler'

const router = useRouter()
const keyword = ref('')
const activeCategory = ref('全部')
const sortBy = ref<'updated' | 'words'>('updated')
const books = ref<BookListItem[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const PAGE_SIZE = 12
const categories = ref<string[]>(['全部'])

const sortOptions = [
  { value: 'updated' as const, label: '最近更新', icon: PhClock },
  { value: 'words' as const, label: '字数', icon: PhTextAa },
]

let debounceTimer: ReturnType<typeof setTimeout> | null = null

async function loadBooks(reset = false) {
  if (reset) page.value = 1
  loading.value = true
  try {
    const result = await fetchBookList({
      category: activeCategory.value,
      keyword: keyword.value.trim() || undefined,
      sort: sortBy.value,
      page: page.value,
      pageSize: PAGE_SIZE,
    })
    books.value = reset ? result.items : [...books.value, ...result.items]
    total.value = result.total
  } catch (e) {
    handleError(e)
  } finally {
    loading.value = false
  }
}

function loadMore() {
  page.value += 1
  loadBooks(false)
}

onMounted(async () => {
  try {
    categories.value = await fetchBookCategories()
  } catch {
    categories.value = ['全部', '玄幻', '都市', '科幻', '悬疑', '言情', '历史']
  }
  loadBooks(true)
})

watch([activeCategory, sortBy], () => loadBooks(true))

watch(keyword, () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadBooks(true), 300)
})

function goBook(id: number) {
  router.push(`/book/${id}`)
}

function resetFilters() {
  keyword.value = ''
  activeCategory.value = '全部'
  sortBy.value = 'updated'
  loadBooks(true)
}
</script>

<style scoped>
.square-header {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border-soft);
}

@media (min-width: 768px) {
  .square-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.search-box {
  position: relative;
  width: 100%;
  max-width: 320px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 42px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition), box-shadow var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px var(--color-accent-soft);
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 28px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.sort-row {
  padding-top: 4px;
}

.filter-row-label {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-right: 4px;
  flex-shrink: 0;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  border-radius: var(--radius-full);
  font-size: 13px;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  transition: all var(--transition);
}

.filter-chip:hover {
  border-color: var(--color-accent-muted);
  color: var(--color-text);
}

.filter-chip.active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.load-more {
  margin-top: 32px;
  text-align: center;
}

.book-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}
</style>
