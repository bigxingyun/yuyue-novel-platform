<template>
  <div class="sub-page page-container">
    <SubPageHeader title="经验记录" />

    <section v-if="userStore.userInfo" class="exp-summary card">
      <TitleBadge
        :level="titleInfo.level"
        :title="titleInfo.title"
        variant="accent"
        :show-level="true"
      />
      <ExpProgressBar
        :progress="titleInfo.progress"
        :exp-to-next="titleInfo.expToNext"
        :label="`累计 ${userStore.userInfo.exp} 经验`"
      />
    </section>

    <ul v-if="items.length" class="exp-list">
      <li v-for="item in items" :key="item.id" class="exp-item card">
        <div>
          <span class="exp-source">{{ item.source }}</span>
          <span class="exp-time">{{ item.time }}</span>
        </div>
        <span class="exp-amount">+{{ item.amount }}</span>
      </li>
    </ul>

    <p v-else-if="!loading" class="empty-hint">暂无经验记录</p>
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
import ExpProgressBar from '@/components/common/ExpProgressBar.vue'
import SubPageHeader from '@/components/common/SubPageHeader.vue'
import TitleBadge from '@/components/common/TitleBadge.vue'
import { fetchExpLogs, type ExpLogItem } from '@/api/profile'
import { getTitleInfo } from '@/constants/titles'
import { useUserStore } from '@/stores/user'
import { handleError } from '@/utils/errorHandler'

const userStore = useUserStore()
const items = ref<ExpLogItem[]>([])
const page = ref(1)
const total = ref(0)
const pageSize = 20
const loading = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const titleInfo = computed(() => getTitleInfo(userStore.userInfo?.exp ?? 0))

async function load() {
  loading.value = true
  try {
    const result = await fetchExpLogs(page.value, pageSize)
    items.value = result.items
    total.value = result.total
  } catch (e) {
    handleError(e)
  } finally {
    loading.value = false
  }
}

function goPage(next: number) {
  page.value = next
  load()
}

onMounted(load)
</script>

<style scoped>
.exp-summary {
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-width: 560px;
}

.exp-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  max-width: 560px;
}

.exp-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
}

.exp-source {
  display: block;
  font-size: var(--text-base);
  margin-bottom: 4px;
}

.exp-time {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.exp-amount {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-accent);
}

.empty-hint {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.pager-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  margin-top: var(--space-5);
  max-width: 560px;
}

.pager-info {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  min-width: 72px;
  text-align: center;
}
</style>
