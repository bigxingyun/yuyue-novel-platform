<template>
  <div class="admin-page">
    <div class="admin-page-header">
      <h1 class="admin-title">密钥管理</h1>
    </div>

    <section class="admin-section card">
      <h2 class="section-head">批量生成注册码</h2>
      <p class="section-desc">生成后请将完整注册码分发给用户，格式为 YUYUE-XXXXXXXX</p>
      <div class="admin-form-row">
        <label class="form-label">数量</label>
        <input
          v-model.number="genCount"
          type="number"
          min="1"
          max="50"
          class="field-input narrow"
        />
        <label class="form-label">有效期（天）</label>
        <input
          v-model.number="expireDays"
          type="number"
          min="1"
          max="365"
          class="field-input narrow"
          placeholder="留空=永久"
        />
        <button class="btn btn-primary btn-sm" :disabled="generating" @click="generate">
          {{ generating ? '生成中…' : '生成注册码' }}
        </button>
      </div>
      <div v-if="newKeys.length" class="new-keys-banner">
        <p>已生成 {{ newKeys.length }} 个注册码，请立即复制保存</p>
        <div class="new-keys-list">
          <div v-for="k in newKeys" :key="k.id" class="new-key-row">
            <code class="key-code-cell">{{ k.code }}</code>
            <button class="btn btn-ghost btn-sm" @click="copyCode(k.code)">复制</button>
          </div>
        </div>
      </div>
    </section>

    <section class="admin-section card">
      <div class="section-head-row">
        <div>
          <h2 class="section-head">注册码列表</h2>
          <p class="section-desc inline">共 {{ keyTotal }} 条</p>
        </div>
        <button class="btn btn-secondary btn-sm" :disabled="exporting" @click="exportCsv">
          {{ exporting ? '导出中…' : '导出 CSV' }}
        </button>
      </div>

      <div v-if="loadingKeys && !keys.length" class="admin-hint">加载中…</div>
      <div v-else-if="keys.length" class="admin-table-wrap admin-table-scroll">
        <table class="admin-table">
          <thead>
            <tr>
              <th>注册码</th>
              <th>状态</th>
              <th>使用者 ID</th>
              <th>创建时间</th>
              <th>过期时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="k in keys" :key="k.id">
              <td class="key-code-cell">{{ k.code }}</td>
              <td>
                <span class="status-tag" :class="k.status">{{ keyStatusLabel(k.status) }}</span>
              </td>
              <td>{{ k.usedBy ?? '—' }}</td>
              <td>{{ k.createdAt || '—' }}</td>
              <td>{{ k.expiresAt || '永久' }}</td>
              <td>
                <button
                  v-if="k.status === 'unused'"
                  class="btn btn-ghost btn-sm"
                  @click="copyCode(k.code)"
                >
                  复制
                </button>
                <span v-else class="admin-hint">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="admin-hint">暂无注册码，请先生成</p>

      <div v-if="keyTotalPages > 1" class="pager-bar">
        <button
          class="btn btn-secondary btn-sm"
          :disabled="loadingKeys || keyPage <= 1"
          @click="goKeyPage(keyPage - 1)"
        >
          上一页
        </button>
        <span class="pager-info">{{ keyPage }} / {{ keyTotalPages }}</span>
        <button
          class="btn btn-secondary btn-sm"
          :disabled="loadingKeys || keyPage >= keyTotalPages"
          @click="goKeyPage(keyPage + 1)"
        >
          下一页
        </button>
      </div>
    </section>

    <section class="admin-section card">
      <h2 class="section-head">生成找回密钥</h2>
      <p class="section-desc">搜索用户后生成一次性找回密钥（7 天有效），用户可在找回密码页使用</p>
      <div class="admin-form-row">
        <input
          v-model="userKeyword"
          class="field-input user-select"
          type="search"
          placeholder="搜索昵称或用户 ID"
          @input="onUserSearchInput"
        />
        <select v-model.number="recoveryUserId" class="field-input user-select">
          <option :value="null" disabled>选择用户</option>
          <option v-for="u in userOptions" :key="u.id" :value="u.id">
            {{ u.nickname }}（ID {{ u.id }}）
          </option>
        </select>
        <button
          class="btn btn-secondary btn-sm"
          :disabled="!recoveryUserId || generatingRecovery"
          @click="genRecovery"
        >
          {{ generatingRecovery ? '生成中…' : '生成找回密钥' }}
        </button>
      </div>
      <div v-if="recoveryKey" class="recovery-result">
        <span>用户 <strong>{{ recoveryKey.nickname }}</strong> 的找回密钥（7 天内有效）：</span>
        <code class="key-code-cell">{{ recoveryKey.code }}</code>
        <button class="btn btn-ghost btn-sm" @click="copyCode(recoveryKey.code)">复制</button>
        <button class="btn btn-ghost btn-sm" @click="recoveryKey = null">关闭</button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  fetchAdminUsers,
  fetchRegistrationKeys,
  generateRecoveryKey,
  generateRegistrationKeys,
  type AdminUser,
  type RegistrationKey,
} from '@/api/admin'
import { handleError, notify } from '@/utils/errorHandler'

const genCount = ref(1)
const expireDays = ref<number | null>(null)
const generating = ref(false)
const exporting = ref(false)
const generatingRecovery = ref(false)
const loadingKeys = ref(true)
const newKeys = ref<RegistrationKey[]>([])
const keys = ref<RegistrationKey[]>([])
const keyPage = ref(1)
const keyTotal = ref(0)
const keyPageSize = 20
const userOptions = ref<AdminUser[]>([])
const userKeyword = ref('')
const recoveryUserId = ref<number | null>(null)
const recoveryKey = ref<{ code: string; nickname: string } | null>(null)

let userSearchTimer: ReturnType<typeof setTimeout> | null = null

const keyTotalPages = computed(() => Math.max(1, Math.ceil(keyTotal.value / keyPageSize)))

function keyStatusLabel(status: string) {
  return { unused: '未使用', used: '已使用', expired: '已过期' }[status] ?? status
}

async function copyCode(code: string) {
  try {
    await navigator.clipboard.writeText(code)
    notify('已复制到剪贴板', 'success')
  } catch {
    notify('复制失败，请手动复制')
  }
}

async function loadKeys() {
  loadingKeys.value = true
  try {
    const result = await fetchRegistrationKeys(keyPage.value, keyPageSize)
    keys.value = result.items
    keyTotal.value = result.total
  } catch (e) {
    handleError(e)
  } finally {
    loadingKeys.value = false
  }
}

function reloadKeys() {
  keyPage.value = 1
  loadKeys()
}

function goKeyPage(next: number) {
  keyPage.value = next
  loadKeys()
}

async function loadUsers(keyword = '') {
  try {
    const result = await fetchAdminUsers(1, 50, keyword)
    userOptions.value = result.items
    if (recoveryUserId.value && !result.items.some((u) => u.id === recoveryUserId.value)) {
      recoveryUserId.value = null
    }
  } catch (e) {
    handleError(e)
  }
}

function onUserSearchInput() {
  if (userSearchTimer) clearTimeout(userSearchTimer)
  userSearchTimer = setTimeout(() => {
    void loadUsers(userKeyword.value)
  }, 300)
}

onMounted(() => {
  loadKeys()
  loadUsers()
})

async function generate() {
  const count = Math.min(50, Math.max(1, genCount.value || 1))
  genCount.value = count
  const days =
    expireDays.value != null && expireDays.value > 0
      ? Math.min(365, Math.max(1, expireDays.value))
      : null
  generating.value = true
  try {
    newKeys.value = await generateRegistrationKeys(count, days)
    notify(`已生成 ${newKeys.value.length} 个注册码`, 'success')
    reloadKeys()
  } catch (e) {
    handleError(e)
  } finally {
    generating.value = false
  }
}

function csvEscape(value: string | number | null | undefined) {
  const text = String(value ?? '')
  if (/[",\n]/.test(text)) return `"${text.replace(/"/g, '""')}"`
  return text
}

async function exportCsv() {
  exporting.value = true
  try {
    const all: RegistrationKey[] = []
    let page = 1
    const size = 50
    while (true) {
      const result = await fetchRegistrationKeys(page, size)
      all.push(...result.items)
      if (page * size >= result.total) break
      page += 1
    }
    const lines = [
      ['注册码', '状态', '使用者ID', '创建时间', '过期时间'].join(','),
      ...all.map((k) =>
        [
          csvEscape(k.code),
          csvEscape(keyStatusLabel(k.status)),
          csvEscape(k.usedBy),
          csvEscape(k.createdAt),
          csvEscape(k.expiresAt || '永久'),
        ].join(','),
      ),
    ]
    const blob = new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `registration-keys-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    notify(`已导出 ${all.length} 条记录`, 'success')
  } catch (e) {
    handleError(e)
  } finally {
    exporting.value = false
  }
}

async function genRecovery() {
  if (!recoveryUserId.value) {
    notify('请选择用户')
    return
  }
  generatingRecovery.value = true
  try {
    const result = await generateRecoveryKey(recoveryUserId.value)
    recoveryKey.value = { code: result.code, nickname: result.nickname }
    notify('找回密钥已生成', 'success')
  } catch (e) {
    handleError(e)
  } finally {
    generatingRecovery.value = false
  }
}
</script>

<style scoped>
.section-desc {
  margin: -6px 0 14px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.section-desc.inline {
  margin: 4px 0 0;
}

.section-head-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.section-head-row .section-head {
  margin-bottom: 0;
}

.form-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.user-select {
  min-width: 220px;
  max-width: 360px;
}

.admin-table-scroll {
  max-height: min(52dvh, 480px);
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

.recovery-result {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
  padding: 12px 14px;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-md);
  font-size: 14px;
}
</style>
