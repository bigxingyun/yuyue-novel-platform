<template>
  <img
    :src="displaySrc"
    :alt="alt"
    class="user-avatar"
    :class="[`size-${size}`]"
    loading="lazy"
    @error="onError"
  />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { defaultAvatarUrl } from '@/constants/titles'

const props = withDefaults(
  defineProps<{
    src?: string | null
    seed?: number | string
    alt?: string
    size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  }>(),
  {
    src: '',
    seed: 'yuyue',
    alt: '',
    size: 'md',
  },
)

const errored = ref(false)

watch(
  () => props.src,
  () => {
    errored.value = false
  },
)

const displaySrc = computed(() => {
  if (!errored.value && props.src?.trim()) return props.src
  return defaultAvatarUrl(props.seed)
})

function onError() {
  errored.value = true
}
</script>

<style scoped>
.user-avatar {
  border-radius: var(--radius-full);
  object-fit: cover;
  flex-shrink: 0;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-soft);
}

.size-xs {
  width: 24px;
  height: 24px;
}

.size-sm {
  width: 32px;
  height: 32px;
}

.size-md {
  width: 40px;
  height: 40px;
}

.size-lg {
  width: 56px;
  height: 56px;
}

.size-xl {
  width: 72px;
  height: 72px;
}
</style>
