<template>
  <div class="exp-progress">
    <div v-if="showLabel" class="exp-progress-head">
      <span class="exp-progress-label">{{ label }}</span>
      <span v-if="expToNext > 0" class="exp-progress-meta">距下一级 {{ expToNext }} 经验</span>
      <span v-else class="exp-progress-meta">已满级</span>
    </div>
    <div class="exp-progress-track">
      <div class="exp-progress-fill" :style="{ width: `${pct}%` }" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    progress?: number
    expToNext?: number
    label?: string
    showLabel?: boolean
  }>(),
  {
    progress: 0,
    expToNext: 0,
    label: '升级进度',
    showLabel: true,
  },
)

const pct = computed(() => Math.round(Math.min(1, Math.max(0, props.progress)) * 100))
</script>

<style scoped>
.exp-progress {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.exp-progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  font-size: var(--text-xs);
}

.exp-progress-label {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.exp-progress-meta {
  color: var(--color-text-muted);
}

.exp-progress-track {
  height: 6px;
  border-radius: var(--radius-full);
  background: var(--color-border-soft);
  overflow: hidden;
}

.exp-progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  background: linear-gradient(90deg, var(--color-accent), #b8435f);
  transition: width var(--transition);
}
</style>
