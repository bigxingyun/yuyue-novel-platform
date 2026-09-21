<template>
  <div class="comment-block" :class="{ compact, reply: !!comment.parentId }">
    <div class="comment-layout">
      <UserAvatar :src="comment.avatar" :seed="comment.userId" size="sm" class="comment-avatar" />
      <div class="comment-main">
        <div class="comment-head">
          <div class="comment-user-wrap">
            <span class="comment-user">{{ comment.user }}</span>
            <TitleBadge
              v-if="comment.title"
              :level="comment.level ?? 1"
              :title="comment.title"
              compact
              :show-icon="false"
              :show-level="false"
              variant="muted"
            />
            <span v-if="comment.isPinned" class="pinned-badge">置顶</span>
            <span v-if="comment.isPinned" class="author-badge">作者</span>
          </div>
          <div v-if="showActions" class="comment-actions">
            <button v-if="canReply" type="button" class="action-link" @click="$emit('reply', comment)">
              回复
            </button>
            <button v-if="canPinAction" type="button" class="action-link" @click="$emit('pin', comment)">
              置顶
            </button>
            <button v-if="canDelete" type="button" class="action-link danger" @click="$emit('delete', comment)">
              删除
            </button>
          </div>
        </div>
        <p class="comment-body">{{ comment.content }}</p>
        <div v-if="comment.replies?.length" class="comment-replies">
          <CommentItemRow
            v-for="r in comment.replies"
            :key="r.id"
            :comment="r"
            :type="type"
            :can-pin="canPin"
            :compact="true"
            @reply="$emit('reply', $event)"
            @pin="$emit('pin', $event)"
            @delete="$emit('delete', $event)"
          />
        </div>
        <div v-if="replyingTo?.id === comment.id" class="reply-compose">
          <textarea v-model="replyText" class="field-input" rows="2" placeholder="写下回复…" />
          <div class="reply-actions">
            <button type="button" class="btn btn-ghost btn-sm" @click="$emit('cancel-reply')">取消</button>
            <button type="button" class="btn btn-primary btn-sm" @click="submitReply">发送</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import TitleBadge from '@/components/common/TitleBadge.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import type { CommentItem } from '@/types/comment'
import { useUserStore } from '@/stores/user'
import { UserRole } from '@/types/enums'

defineOptions({ name: 'CommentItemRow' })

const props = defineProps<{
  comment: CommentItem
  type: 'paragraph' | 'chapter' | 'book'
  canPin?: boolean
  compact?: boolean
  replyingTo?: CommentItem | null
}>()

const emit = defineEmits<{
  reply: [comment: CommentItem]
  pin: [comment: CommentItem]
  delete: [comment: CommentItem]
  'submit-reply': [parent: CommentItem, text: string]
  'cancel-reply': []
}>()

const userStore = useUserStore()
const replyText = ref('')

const isAdmin = computed(
  () =>
    userStore.userInfo?.role === UserRole.ADMIN ||
    userStore.userInfo?.role === UserRole.SUPERADMIN,
)

const canReply = computed(() => !props.comment.parentId)
const canDelete = computed(
  () =>
    !!userStore.userInfo &&
    (props.comment.userId === userStore.userInfo.id || isAdmin.value || props.canPin),
)
const canPinAction = computed(() => !!props.canPin && !props.comment.parentId)
const showActions = computed(() => canReply.value || canDelete.value || canPinAction.value)

function submitReply() {
  const text = replyText.value.trim()
  if (!text) return
  emit('submit-reply', props.comment, text)
  replyText.value = ''
}
</script>

<style scoped>
.comment-block {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  background: var(--color-bg);
}

.comment-block.compact,
.comment-replies .comment-block {
  background: var(--color-bg-elevated);
  margin-top: var(--space-2);
}

.comment-layout {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
}

.comment-main {
  flex: 1;
  min-width: 0;
}

.comment-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.comment-user-wrap {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.comment-user {
  font-size: var(--text-sm);
  font-weight: 600;
}

.comment-actions {
  display: flex;
  gap: var(--space-2);
  flex-shrink: 0;
}

.action-link {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  padding: 0;
}

.action-link:hover {
  color: var(--color-accent);
}

.action-link.danger:hover {
  color: #b43c3c;
}

.comment-body {
  font-size: var(--text-sm);
  line-height: 1.6;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
}

.comment-replies {
  margin-top: var(--space-2);
  padding-left: var(--space-2);
  border-left: 2px solid var(--color-border-soft);
}

.pinned-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 500;
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.author-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 500;
  background: #e8efe4;
  color: #3d5a3a;
}

.reply-compose {
  margin-top: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
</style>
