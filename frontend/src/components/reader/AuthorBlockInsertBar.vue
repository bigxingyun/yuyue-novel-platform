<template>
  <button type="button" class="author-insert-bar" @click.stop="$emit('insert')">
    <PhPlus :size="14" weight="bold" />
    <span>插入图片</span>
  </button>
</template>

<script setup lang="ts">
import { PhPlus } from '@phosphor-icons/vue'

defineEmits<{ insert: [] }>()
</script>

<style scoped>
.author-insert-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  min-height: 36px;
  margin: 0.2em 0 0.8em;
  padding: 6px 12px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  background: transparent;
  transition:
    border-color var(--transition),
    color var(--transition),
    background var(--transition);
}

.author-insert-bar:hover {
  border-color: var(--color-accent-muted);
  color: var(--color-accent);
  background: var(--color-accent-soft);
}
</style>
