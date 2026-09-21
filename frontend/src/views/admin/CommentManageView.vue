<template>
  <div class="admin-page comment-admin">
    <div class="admin-page-header">
      <div>
        <h1 class="admin-title">评论审核</h1>
        <p class="admin-subtitle">
          共 {{ total }} 条{{ visibilityLabel }}
          <span v-if="total > 0"> · 第 {{ page }} / {{ totalPages }} 页</span>
        </p>
      </div>
      <button class="btn btn-ghost btn-sm" :disabled="loading" @click="reload">
        {{ loading ? '刷新中…' : '刷新' }}
      </button>
    </div>

    <div class="comment-toolbar card">
      <div class="type-tabs">
        <button
          v-for="t in types"
          :key="t.value"
          class="btn btn-sm"
          :class="activeType === t.value ? 'btn-primary' : 'btn-ghost'"
          @click="switchType(t.value)"
        >
          {{ t.label }}
        </button>
      </div>
      <div class="visibility-tabs">
        <button
          v-for="v in visibilityOptions"
          :key="v.value"
          class="btn btn-sm"
          :class="visibility === v.value ? 'btn-primary' : 'btn-ghost'"
          @click="switchVisibility(v.value)"
        >
          {{ v.label }}
        </button>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <PhMagnifyingGlass :size="16" class="search-icon" />
          <input
            v-model="keyword"
            class="search-input field-input"
            type="search"
            placeholder="搜索用户、书名、章节或内容…"
          />
        </div>
        <select v-model.number="pageSize" class="page-size-select field-input" @change="reload">
          <option :value="20">20 条/页</option>
          <option :value="50">50 条/页</option>
        </select>
      </div>
    </div>

    <div v-if="loading && !items.length" class="state-hint card">加载中…</div>

    <EmptyState
      v-else-if="!items.length"
      :icon="PhChatCircle"
      title="暂无评论"
      :description="emptyDescription"
    />

    <div v-else class="admin-table-wrap card comment-table-wrap">
      <table class="admin-table comment-table">
        <thead>
          <tr>
            <th class="col-id">ID</th>
            <th class="col-user">用户</th>
            <th class="col-context">来源</th>
            <th class="col-content">内容</th>
            <th class="col-status">状态</th>
            <th class="col-time">时间</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in items" :key="c.id">
            <td class="col-id">{{ c.id }}</td>
            <td class="col-user">
              <div class="user-cell">
                <UserAvatar :src="c.avatar" :seed="c.userId" size="xs" />
                <div>
                  <span class="user-name">{{ c.user }}</span>
                  <span class="user-id">#{{ c.userId }}</span>
                </div>
              </div>
            </td>
            <td class="col-context wrap">
              <RouterLink :to="`/book/${c.bookId}`" class="context-link" target="_blank">
                {{ c.bookTitle }}
              </RouterLink>
              <span v-if="c.chapterTitle" class="context-sub">{{ c.chapterTitle }}</span>
              <span v-if="c.paragraphIndex != null" class="context-sub">
                第 {{ c.paragraphIndex + 1 }} 段
              </span>
            </td>
            <td class="col-content wrap">
              <p class="content-preview">{{ preview(c.content) }}</p>
              <button
                v-if="c.content.length > previewLen"
                type="button"
                class="link-btn"
                @click="openDetail(c)"
              >
                查看全文
              </button>
            </td>
            <td class="col-status">
              <span class="status-tag" :class="c.isHidden ? 'unpublished' : 'published'">
                {{ c.isHidden ? '已隐藏' : '正常' }}
              </span>
            </td>
            <td class="col-time">{{ c.createdAt }}</td>
            <td class="col-actions">
              <button
                v-if="!c.isHidden"
                class="btn btn-ghost btn-sm danger-btn"
                :disabled="actingId === c.id"
                @click="hide(c)"
              >
                {{ actingId === c.id ? '处理中…' : '隐藏' }}
              </button>
              <button
                v-else
                class="btn btn-ghost btn-sm"
                :disabled="actingId === c.id"
                @click="unhide(c)"
              >
                {{ actingId === c.id ? '处理中…' : '恢复' }}
              </button>
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

    <Transition name="modal">
      <div v-if="detailItem" class="detail-modal" @click="detailItem = null">
        <div class="detail-card card" @click.stop>
          <header class="detail-head">
            <h2>评论详情</h2>
            <button type="button" class="btn btn-ghost btn-sm" @click="detailItem = null">关闭</button>
          </header>
          <dl class="detail-meta">
            <div><dt>ID</dt><dd>{{ detailItem.id }}</dd></div>
            <div><dt>用户</dt><dd>{{ detailItem.user }} (#{{ detailItem.userId }})</dd></div>
            <div><dt>书籍</dt><dd>{{ detailItem.bookTitle }}</dd></div>
            <div v-if="detailItem.chapterTitle"><dt>章节</dt><dd>{{ detailItem.chapterTitle }}</dd></div>
            <div v-if="detailItem.paragraphIndex != null">
              <dt>段落</dt><dd>第 {{ detailItem.paragraphIndex + 1 }} 段</dd>
            </div>
            <div><dt>时间</dt><dd>{{ detailItem.createdAt }}</dd></div>
          </dl>
          <p class="detail-content">{{ detailItem.content }}</p>
          <div class="detail-actions">
            <button
              v-if="!detailItem.isHidden"
              class="btn btn-ghost btn-sm danger-btn"
              :disabled="actingId === detailItem.id"
              @click="hide(detailItem)"
            >
              隐藏该评论
            </button>
            <button
              v-else
              class="btn btn-ghost btn-sm"
              :disabled="actingId === detailItem.id"
              @click="unhide(detailItem)"
            >
              恢复显示
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { PhChatCircle, PhMagnifyingGlass } from '@phosphor-icons/vue'
import EmptyState from '@/components/common/EmptyState.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { fetchAdminComments, hideAdminComment, unhideAdminComment, type AdminComment } from '@/api/admin'
import { handleError, notify } from '@/utils/errorHandler'

const types = [
  { value: 'chapter' as const, label: '章评' },
  { value: 'paragraph' as const, label: '段评' },
  { value: 'book' as const, label: '书评' },
]

const visibilityOptions = [
  { value: 'visible' as const, label: '正常' },
  { value: 'hidden' as const, label: '已隐藏' },
]

const previewLen = 80

const activeType = ref<'chapter' | 'paragraph' | 'book'>('chapter')
const visibility = ref<'visible' | 'hidden'>('visible')
const items = ref<AdminComment[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const keyword = ref('')
const loading = ref(false)
const actingId = ref<number | null>(null)
const detailItem = ref<AdminComment | null>(null)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const visibilityLabel = computed(() => (visibility.value === 'hidden' ? '已隐藏评论' : '正常评论'))

const emptyDescription = computed(() => {
  if (keyword.value) return '没有匹配的评论，试试调整关键词'
  return visibility.value === 'hidden' ? '当前分类下没有已隐藏评论' : '当前分类下没有正常评论'
})

function preview(text: string) {
  if (text.length <= previewLen) return text
  return `${text.slice(0, previewLen)}…`
}

async function load() {
  loading.value = true
  try {
    const result = await fetchAdminComments(activeType.value, page.value, {
      pageSize: pageSize.value,
      keyword: keyword.value,
      visibility: visibility.value,
    })
    items.value = result.items
    total.value = result.total
    if (page.value > totalPages.value && totalPages.value > 0) {
      page.value = totalPages.value
      await load()
    }
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

watch(keyword, () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(reload, 300)
})

function switchType(type: 'chapter' | 'paragraph' | 'book') {
  if (activeType.value === type) return
  activeType.value = type
  reload()
}

function switchVisibility(next: 'visible' | 'hidden') {
  if (visibility.value === next) return
  visibility.value = next
  reload()
}

function goPage(next: number) {
  page.value = next
  load()
}

function openDetail(item: AdminComment) {
  detailItem.value = item
}

async function hide(comment: AdminComment) {
  if (!confirm('确定隐藏该评论？隐藏后读者端将不再显示，可在「已隐藏」中恢复。')) return
  actingId.value = comment.id
  try {
    await hideAdminComment(comment.id, activeType.value)
    notify('已隐藏', 'success')
    if (detailItem.value?.id === comment.id) detailItem.value = null
    await load()
  } catch (e) {
    handleError(e)
  } finally {
    actingId.value = null
  }
}

async function unhide(comment: AdminComment) {
  if (!confirm('确定恢复显示该评论？')) return
  actingId.value = comment.id
  try {
    await unhideAdminComment(comment.id, activeType.value)
    notify('已恢复显示', 'success')
    if (detailItem.value?.id === comment.id) detailItem.value = null
    await load()
  } catch (e) {
    handleError(e)
  } finally {
    actingId.value = null
  }
}
</script>

<style scoped>
.admin-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--color-text-muted);
}

.comment-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  margin-bottom: 16px;
}

.type-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.visibility-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  min-width: 240px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  min-width: 240px;
  padding-left: 36px;
}

.page-size-select {
  width: 110px;
  min-width: 110px;
}

.state-hint {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-muted);
}

.comment-table-wrap {
  max-height: calc(100dvh - 280px);
  overflow: auto;
}

.comment-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
}

.col-id {
  width: 64px;
}

.col-user {
  min-width: 120px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-context {
  min-width: 160px;
  max-width: 220px;
}

.col-content {
  min-width: 280px;
  max-width: 420px;
}

.col-status {
  width: 88px;
}

.col-time {
  width: 130px;
}

.col-actions {
  width: 88px;
}

.user-name {
  display: block;
  font-weight: 500;
}

.user-id {
  font-size: 12px;
  color: var(--color-text-muted);
}

.context-link {
  display: block;
  color: var(--color-accent);
  font-weight: 500;
}

.context-link:hover {
  text-decoration: underline;
}

.context-sub {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-muted);
}

.content-preview {
  margin: 0;
  line-height: 1.55;
  white-space: pre-wrap;
  word-break: break-word;
}

.link-btn {
  margin-top: 6px;
  padding: 0;
  font-size: 12px;
  color: var(--color-accent);
}

.danger-btn {
  color: #b43c3c;
}

.danger-btn:hover:not(:disabled) {
  background: rgba(180, 60, 60, 0.08);
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

.detail-modal {
  position: fixed;
  inset: 0;
  z-index: 600;
  background: rgba(20, 23, 30, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.detail-card {
  width: 100%;
  max-width: 560px;
  max-height: min(80dvh, 640px);
  overflow: auto;
  padding: 20px 24px;
}

.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-head h2 {
  margin: 0;
  font-size: 18px;
  font-family: var(--font-serif);
}

.detail-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 16px;
  margin: 0 0 16px;
}

.detail-meta div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-meta dt {
  font-size: 11px;
  color: var(--color-text-muted);
}

.detail-meta dd {
  margin: 0;
  font-size: 14px;
}

.detail-content {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  background: var(--color-bg);
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
