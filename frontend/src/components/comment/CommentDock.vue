<template>
  <section class="comment-dock" :class="{ 'comment-dock-side': side, 'comment-dock-inline': inline }">
    <header class="comment-dock-header">
      <h3 class="comment-dock-title">{{ title }}</h3>
      <span v-if="count != null" class="comment-dock-count">{{ count }} 条</span>
    </header>

    <div class="comment-dock-list">
      <slot name="empty" />
      <slot name="list" />
    </div>

    <footer v-if="$slots.compose" class="comment-dock-compose">
      <slot name="compose" />
    </footer>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  count?: number
  /** 桌面端侧栏模式（书主页书评） */
  side?: boolean
  /** 章末内联模式（阅读页章评） */
  inline?: boolean
}>()
</script>

<style scoped>
.comment-dock {
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border-soft);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.comment-dock-side {
  height: 100%;
  max-height: calc(100dvh - var(--header-height) - 48px);
}

.comment-dock-inline {
  max-height: min(50dvh, 420px);
}

.comment-dock-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--color-border-soft);
  background: var(--color-bg-elevated);
}

.comment-dock-title {
  font-family: var(--font-serif);
  font-size: 16px;
  font-weight: 600;
}

.comment-dock-count {
  font-size: 12px;
  color: var(--color-text-muted);
}

.comment-dock-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 12px 14px;
  -webkit-overflow-scrolling: touch;
}

.comment-dock-compose {
  flex-shrink: 0;
  padding: 12px 14px 14px;
  border-top: 1px solid var(--color-border-soft);
  background: var(--color-bg-elevated);
}
</style>
