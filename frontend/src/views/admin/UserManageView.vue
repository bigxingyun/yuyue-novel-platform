<template>
  <div class="admin-page">
    <div class="admin-page-header">
      <div>
        <h1 class="admin-title">用户管理</h1>
        <p class="admin-subtitle">
          共 {{ total }} 位用户
          <span v-if="totalPages > 1"> · 第 {{ page }} / {{ totalPages }} 页</span>
        </p>
      </div>
      <button class="btn btn-ghost btn-sm" :disabled="loading" @click="reload">刷新</button>
    </div>

    <div v-if="loading && !users.length" class="state-hint card">加载中…</div>

    <div v-else class="admin-table-wrap card admin-table-scroll">
      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>昵称</th>
            <th>角色</th>
            <th>状态</th>
            <th>经验</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.nickname }}</td>
            <td>
              <select
                v-if="isSuperAdmin && u.id !== currentUserId"
                class="role-select field-input"
                :value="u.role"
                @change="changeRole(u.id, ($event.target as HTMLSelectElement).value)"
              >
                <option value="user">读者</option>
                <option value="author">作者</option>
                <option value="admin">管理员</option>
              </select>
              <span v-else>{{ roleLabel(u.role) }}</span>
            </td>
            <td>
              <span class="status-tag" :class="u.status === 'active' ? 'active' : 'banned'">
                {{ u.status === 'active' ? '正常' : '封禁' }}
              </span>
            </td>
            <td>{{ u.exp }}</td>
            <td>{{ u.createdAt || '—' }}</td>
            <td>
              <div class="admin-actions">
                <button
                  v-if="u.status === 'active' && u.id !== currentUserId"
                  class="btn btn-ghost btn-sm"
                  @click="toggleBan(u.id, 'banned')"
                >
                  封禁
                </button>
                <button
                  v-else-if="u.status !== 'active'"
                  class="btn btn-ghost btn-sm"
                  @click="toggleBan(u.id, 'active')"
                >
                  解封
                </button>
                <span v-else-if="u.id === currentUserId" class="admin-hint">当前账号</span>
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
import { fetchAdminUsers, updateUserRole, updateUserStatus, type AdminUser } from '@/api/admin'
import { useUserStore } from '@/stores/user'
import { UserRole } from '@/types/enums'
import { handleError, notify } from '@/utils/errorHandler'

const userStore = useUserStore()
const users = ref<AdminUser[]>([])
const page = ref(1)
const total = ref(0)
const pageSize = 20
const loading = ref(false)

const currentUserId = computed(() => userStore.userInfo?.id)
const isSuperAdmin = computed(() => userStore.userInfo?.role === UserRole.SUPERADMIN)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

function roleLabel(role: string) {
  return {
    guest: '访客',
    user: '读者',
    author: '作者',
    admin: '管理员',
    superadmin: '超级管理员',
  }[role] ?? role
}

async function load() {
  loading.value = true
  try {
    const result = await fetchAdminUsers(page.value, pageSize)
    users.value = result.items
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

async function toggleBan(userId: number, status: 'active' | 'banned') {
  if (status === 'banned' && !confirm('确定封禁该用户？')) return
  try {
    await updateUserStatus(userId, status)
    notify(status === 'banned' ? '已封禁' : '已解封', 'success')
    await load()
  } catch (e) {
    handleError(e)
  }
}

async function changeRole(userId: number, role: string) {
  if (!confirm(`确定将该用户角色改为「${roleLabel(role)}」？`)) {
    await load()
    return
  }
  try {
    await updateUserRole(userId, role)
    notify('角色已更新', 'success')
    await load()
  } catch (e) {
    handleError(e)
    await load()
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

.role-select {
  width: auto;
  min-width: 90px;
  padding: 4px 8px;
  font-size: 13px;
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
