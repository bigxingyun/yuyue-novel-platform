<template>
  <div class="admin-page">
    <div class="admin-page-header">
      <div>
        <h1 class="admin-title">作者审核</h1>
        <p class="admin-subtitle">
          共 {{ total }} 条申请
          <span v-if="totalPages > 1"> · 第 {{ page }} / {{ totalPages }} 页</span>
        </p>
      </div>
      <button class="btn btn-ghost btn-sm" :disabled="loading" @click="reload">刷新</button>
    </div>

    <div class="status-tabs">
      <button
        v-for="t in statusTabs"
        :key="t.value"
        class="btn btn-sm"
        :class="activeStatus === t.value ? 'btn-primary' : 'btn-ghost'"
        @click="switchStatus(t.value)"
      >
        {{ t.label }}
      </button>
    </div>

    <div v-if="loading && !items.length" class="state-hint card">加载中…</div>

    <ul v-else-if="items.length" class="admin-list">
      <li v-for="app in items" :key="app.id" class="admin-item card">
        <div class="admin-item-head">
          <strong>{{ app.nickname }}</strong>
          <span class="status-tag" :class="app.status">{{ statusLabel(app.status) }}</span>
        </div>
        <p class="admin-item-reason">{{ app.reason }}</p>
        <p class="admin-item-meta">申请时间：{{ app.createdAt }}</p>
        <div v-if="app.status === 'pending'" class="admin-item-actions">
          <button class="btn btn-primary btn-sm" @click="review(app.id, 'approved')">通过</button>
          <button class="btn btn-secondary btn-sm" @click="openReject(app.id)">拒绝</button>
        </div>
        <p v-if="app.reviewNote" class="admin-item-note">备注：{{ app.reviewNote }}</p>
      </li>
    </ul>

    <EmptyState
      v-else
      :icon="PhPenNib"
      title="暂无申请"
      :description="activeStatus === 'pending' ? '当前没有待审核的作者申请' : '该筛选下没有记录'"
    />

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

    <Transition name="modal">
      <div v-if="rejectId" class="reject-modal" @click="rejectId = null">
        <div class="reject-card card" @click.stop>
          <h3 class="reject-title">拒绝申请</h3>
          <textarea
            v-model="rejectNote"
            class="field-input"
            rows="3"
            placeholder="填写拒绝原因（可选）…"
          />
          <div class="reject-actions">
            <button class="btn btn-ghost" @click="rejectId = null">取消</button>
            <button class="btn btn-primary" @click="confirmReject">确认拒绝</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { PhPenNib } from '@phosphor-icons/vue'
import EmptyState from '@/components/common/EmptyState.vue'
import {
  fetchAuthorApplications,
  reviewAuthorApplication,
  type AuthorApplication,
} from '@/api/admin'
import { handleError, notify } from '@/utils/errorHandler'

const statusTabs = [
  { value: 'pending', label: '待审核' },
  { value: 'all', label: '全部' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已拒绝' },
]

const items = ref<AuthorApplication[]>([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const loading = ref(false)
const activeStatus = ref('pending')
const rejectId = ref<number | null>(null)
const rejectNote = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function load() {
  loading.value = true
  try {
    const result = await fetchAuthorApplications(page.value, pageSize, activeStatus.value)
    items.value = result.items
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

function switchStatus(status: string) {
  if (activeStatus.value === status) return
  activeStatus.value = status
  reload()
}

function goPage(next: number) {
  page.value = next
  load()
}

function statusLabel(s: string) {
  return { pending: '待审核', approved: '已通过', rejected: '已拒绝' }[s] ?? s
}

async function review(id: number, status: 'approved' | 'rejected', note?: string) {
  if (status === 'approved' && !confirm('确定通过该申请？')) return
  try {
    await reviewAuthorApplication(id, status, note)
    notify(status === 'approved' ? '已通过' : '已拒绝', 'success')
    await load()
  } catch (e) {
    handleError(e)
  }
}

function openReject(id: number) {
  rejectId.value = id
  rejectNote.value = ''
}

async function confirmReject() {
  if (!rejectId.value) return
  const id = rejectId.value
  rejectId.value = null
  await review(id, 'rejected', rejectNote.value.trim() || undefined)
}
</script>

<style scoped>
.admin-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--color-text-muted);
}

.status-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.state-hint {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-muted);
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

.reject-modal {
  position: fixed;
  inset: 0;
  z-index: 500;
  background: rgba(20, 23, 30, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.reject-card {
  width: 100%;
  max-width: 420px;
  padding: 20px;
}

.reject-title {
  font-size: 16px;
  margin-bottom: 14px;
}

.reject-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}
</style>
