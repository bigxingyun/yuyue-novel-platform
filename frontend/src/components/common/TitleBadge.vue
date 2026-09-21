<template>
  <span class="title-badge" :class="[`variant-${variant}`, { compact }]">
    <PhMedal v-if="showIcon" :size="iconSize" weight="duotone" class="title-icon" />
    <span v-if="showLevel" class="title-level">Lv.{{ level }}</span>
    <span class="title-name">{{ title }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PhMedal } from '@phosphor-icons/vue'

const props = withDefaults(
  defineProps<{
    level?: number
    title?: string
    variant?: 'default' | 'accent' | 'muted'
    compact?: boolean
    showIcon?: boolean
    showLevel?: boolean
  }>(),
  {
    level: 1,
    title: '门外读者',
    variant: 'default',
    compact: false,
    showIcon: true,
    showLevel: false,
  },
)

const iconSize = computed(() => (props.compact ? 12 : 14))
</script>

<style scoped>
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 500;
  line-height: 1.4;
  white-space: nowrap;
}

.title-badge.compact {
  padding: 1px 6px;
  font-size: 10px;
}

.variant-default {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.variant-accent {
  background: linear-gradient(135deg, rgba(139, 41, 66, 0.15), rgba(139, 41, 66, 0.08));
  color: var(--color-accent);
  border: 1px solid var(--color-accent-muted);
}

.variant-muted {
  background: var(--color-bg-elevated);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border-soft);
}

.title-icon {
  flex-shrink: 0;
}

.title-level {
  font-weight: 600;
}
</style>
