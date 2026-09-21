<template>
  <div class="author-image-chrome" :class="{ 'edit-mode': editMode }">
    <ReaderImageBlock :url="url" :alt="alt" />
    <div v-if="editMode" class="image-actions">
      <button type="button" class="image-action-btn" @click.stop="$emit('replace')">
        <PhArrowsClockwise :size="14" />
        替换
      </button>
      <button type="button" class="image-action-btn danger" @click.stop="$emit('remove')">
        <PhTrash :size="14" />
        删除
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PhArrowsClockwise, PhTrash } from '@phosphor-icons/vue'
import ReaderImageBlock from '@/components/reader/ReaderImageBlock.vue'

withDefaults(
  defineProps<{
    url: string
    alt?: string
    editMode?: boolean
  }>(),
  { alt: '章节插图', editMode: false },
)

defineEmits<{ remove: []; replace: [] }>()
</script>

<style scoped>
.author-image-chrome.edit-mode {
  padding: 8px;
  margin: 0.4em 0 1em;
  border: 2px solid var(--color-accent-muted);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-accent-soft) 40%, transparent);
}

.image-actions {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  margin-top: var(--space-2);
}

.image-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border-soft);
  background: var(--color-surface);
}

.image-action-btn:hover {
  color: var(--color-accent);
  border-color: var(--color-accent-muted);
}

.image-action-btn.danger:hover {
  color: #b43c3c;
  border-color: rgba(180, 60, 60, 0.35);
}
</style>
