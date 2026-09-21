<template>
  <div class="admin-page">
    <div class="admin-page-header">
      <div>
        <h1 class="admin-title">书籍管理</h1>
        <p class="admin-subtitle">
          共 {{ total }} 本书
          <span v-if="totalPages > 1"> · 第 {{ page }} / {{ totalPages }} 页</span>
        </p>
      </div>
      <button class="btn btn-ghost btn-sm" :disabled="loading" @click="reload">刷新</button>
    </div>

    <div v-if="loading && !books.length" class="state-hint card">加载中…</div>

    <div v-else class="admin-table-wrap card admin-table-scroll">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>书名</th>
            <th>作者</th>
            <th>分类</th>
            <th>状态</th>
            <th>字数</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in books" :key="b.id">
            <td>{{ b.id }}</td>
            <td class="wrap">{{ b.title }}</td>
            <td>{{ b.author }}</td>
            <td>{{ b.category }}</td>
            <td>
              <span class="status-tag" :class="b.status">{{ statusLabel(b.status) }}</span>
            </td>
            <td>{{ b.wordCount.toLocaleString() }}</td>
            <td>{{ b.updatedAt || '—' }}</td>
            <td>
              <div class="admin-actions">
                <button
                  v-if="b.status === 'published'"
                  class="btn btn-ghost btn-sm"
                  @click="unpublish(b.id)"
                >
                  下架
                </button>
                <button
                  v-else-if="b.status === 'unpublished'"
                  class="btn btn-ghost btn-sm"
                  @click="republish(b.id)"
                >
                  上架
                </button>
                <RouterLink
                  :to="{ name: 'admin-chapters', params: { bookId: b.id } }"
                  class="btn btn-ghost btn-sm"
                >
                  章节
                </RouterLink>
                <button class="btn btn-ghost btn-sm" @click="remove(b)">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

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
import {
  deleteAdminBook,
  fetchAdminBooks,
  updateAdminBookStatus,
  type AdminBook,
} from '@/api/admin'
import { handleError, notify } from '@/utils/errorHandler'

const books = ref<AdminBook[]>([])
const page = ref(1)
const total = ref(0)
const pageSize = 20
const loading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function statusLabel(status: string) {
  return { draft: '草稿', published: '已发布', unpublished: '已下架' }[status] ?? status
}

async function load() {
  loading.value = true
  try {
    const result = await fetchAdminBooks(page.value, pageSize)
    books.value = result.items
    total.value = result.total
  } catch (e) {
    handleError(e)
  } finally {
    loading.value = false
  }
}

function reload() {
  page.value = 1
  load()
}

onMounted(load)

function goPage(next: number) {
  page.value = next
  load()
}

async function unpublish(bookId: number) {
  if (!confirm('确定下架该书籍？作者修改后你可在此重新上架。')) return
  try {
    await updateAdminBookStatus(bookId, 'unpublished')
    notify('已下架', 'success')
    await load()
  } catch (e) {
    handleError(e)
  }
}

async function republish(bookId: number) {
  if (!confirm('确认审核通过并重新上架该书籍？')) return
  try {
    await updateAdminBookStatus(bookId, 'published')
    notify('已重新上架', 'success')
    await load()
  } catch (e) {
    handleError(e)
  }
}

async function remove(book: AdminBook) {
  const input = prompt(`此操作不可恢复。请输入书名「${book.title}」以确认删除：`)
  if (input === null) return
  if (input.trim() !== book.title) {
    notify('书名不匹配，已取消删除')
    return
  }
  try {
    await deleteAdminBook(book.id)
    notify('已删除', 'success')
    if (books.value.length === 1 && page.value > 1) page.value -= 1
    await load()
  } catch (e) {
    handleError(e)
  }
}
</script>

<style scoped>
.admin-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--color-text-muted);
}

.state-hint {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-muted);
}

.admin-table-scroll {
  max-height: calc(100dvh - 220px);
  overflow: auto;
}

.admin-table-scroll :deep(thead th) {
  position: sticky;
  top: 0;
  z-index: 1;
}

.pager-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.pager-info {
  font-size: 13px;
  color: var(--color-text-secondary);
  min-width: 72px;
  text-align: center;
}
</style>
