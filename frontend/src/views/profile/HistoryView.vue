<template>
  <div class="sub-page page-container">
    <SubPageHeader title="阅读历史" />
    <p v-if="total > 0" class="history-meta">共 {{ total }} 条记录</p>

    <ul v-if="items.length" class="history-list">
      <li
        v-for="item in items"
        :key="item.id"
        class="history-item card"
        @click="goRead(item)"
      >
        <img :src="item.cover" alt="" class="history-cover" />
        <div class="history-body">
          <h3>{{ item.title }}</h3>
          <p>{{ item.chapterTitle }}</p>
          <span class="history-time">{{ item.readAt }}</span>
        </div>
        <PhCaretRight :size="18" class="history-arrow" />
      </li>
    </ul>

    <EmptyState
      v-else-if="!loading"
      :icon="PhClockCounterClockwise"
      title="暂无阅读记录"
      description="开始阅读后，历史会出现在这里"
    />

    <p v-else class="empty-hint">加载中…</p>

    <div v-if="totalPages > 1" class="pager-bar">
      <button class="btn btn-secondary btn-sm" :disabled="loading || page <= 1" @click="goPage(page - 1)">
        上一页
      </button>
      <span class="pager-info">{{ page }} / {{ totalPages }}</span>
      <button
        class="btn btn-secondary btn-sm"
        :disabled="loading || page >= totalPages"
        @click="goPage(page + 1)"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { PhCaretRight, PhClockCounterClockwise } from '@phosphor-icons/vue'
import EmptyState from '@/components/common/EmptyState.vue'
import SubPageHeader from '@/components/common/SubPageHeader.vue'
import { fetchReadingHistory, type ReadingHistoryItem } from '@/api/reading'
import { handleError } from '@/utils/errorHandler'

const router = useRouter()
const items = ref<ReadingHistoryItem[]>([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function load() {
  loading.value = true
  try {
    const result = await fetchReadingHistory(page.value, pageSize)
    items.value = result.items
    total.value = result.total
  } catch (e) {
    handleError(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)

function goPage(next: number) {
  page.value = next
  load()
}

function goRead(item: ReadingHistoryItem) {
  router.push(`/read/${item.bookId}/${item.chapterId}`)
}
</script>

<style scoped>
.history-meta {
  margin: -8px 0 16px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  cursor: pointer;
  transition: box-shadow var(--transition);
}

.history-item:hover {
  box-shadow: var(--shadow-md);
}

.history-cover {
  width: 48px;
  height: 68px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.history-body {
  flex: 1;
  min-width: 0;
}

.history-body h3 {
  font-size: 15px;
  margin-bottom: 4px;
}

.history-body p {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.history-time {
  font-size: 12px;
  color: var(--color-text-muted);
}

.history-arrow {
  color: var(--color-text-muted);
}

.empty-hint {
  text-align: center;
  color: var(--color-text-muted);
  padding: 48px 0;
}

.pager-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.pager-info {
  font-size: 13px;
  color: var(--color-text-secondary);
  min-width: 72px;
  text-align: center;
}
</style>
