<template>
  <button type="button" class="chapter-comment-preview" @click.stop="$emit('open')">
    <template v-if="featured">
      <div class="chapter-preview-head">
        <span class="chapter-preview-label">章评</span>
        <span v-if="featured.isPinned" class="chapter-preview-pin">置顶</span>
        <span class="chapter-preview-count">{{ count }} 条</span>
      </div>
      <div class="chapter-preview-user-row">
        <UserAvatar :src="featured.avatar" :seed="featured.userId" size="xs" />
        <span class="chapter-preview-user">{{ featured.user }}</span>
        <TitleBadge
          v-if="featured.title"
          :title="featured.title"
          compact
          :show-icon="false"
          :show-level="false"
          variant="muted"
        />
      </div>
      <p class="chapter-preview-body">{{ featured.content }}</p>
      <p v-if="replyCount > 0" class="chapter-preview-meta">
        {{ replyCount }} 条回复 · 点击查看全部
      </p>
      <p v-else class="chapter-preview-meta">点击查看全部章评</p>
    </template>
    <template v-else>
      <span class="chapter-preview-empty">
        <PhChatCircle :size="18" weight="duotone" />
        写下本章第一条章评
      </span>
    </template>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PhChatCircle } from '@phosphor-icons/vue'
import TitleBadge from '@/components/common/TitleBadge.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import type { CommentItem } from '@/types/comment'
import { replyCountOf } from '@/utils/chapterCommentFeatured'

const props = defineProps<{
  featured: CommentItem | null
  count: number
}>()

defineEmits<{ open: [] }>()

const replyCount = computed(() => (props.featured ? replyCountOf(props.featured) : 0))
</script>

<style scoped>
.chapter-comment-preview {
  display: block;
  width: calc(100% - var(--reader-padding-x, 20px) * 0.2);
  margin: 1.8em auto 0.6em;
  padding: 14px 16px;
  text-align: left;
  border: 1px solid color-mix(in srgb, var(--color-border-soft) 55%, transparent);
  border-radius: var(--radius-md);
  background: color-mix(in srgb, var(--color-surface) 68%, transparent);
  -webkit-backdrop-filter: blur(14px);
  backdrop-filter: blur(14px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
}

.chapter-comment-preview:hover {
  background: color-mix(in srgb, var(--color-surface) 78%, transparent);
  box-shadow: 0 6px 28px rgba(0, 0, 0, 0.08);
}

.chapter-comment-preview:active {
  transform: scale(0.992);
}

.chapter-preview-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.chapter-preview-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--color-accent);
}

.chapter-preview-pin {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.chapter-preview-count {
  margin-left: auto;
  font-size: 11px;
  color: var(--color-text-muted);
}

.chapter-preview-user-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.chapter-preview-user {
  font-size: 13px;
  font-weight: 500;
}

.chapter-preview-body {
  font-size: 14px;
  line-height: 1.55;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.chapter-preview-meta {
  margin-top: 8px;
  font-size: 11px;
  color: var(--color-text-muted);
}

.chapter-comment-preview > span,
.chapter-preview-empty {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-muted);
}
</style>
