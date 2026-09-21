<template>
  <header class="sub-header">
    <button class="back-btn" @click="router.back()">
      <PhArrowLeft :size="20" />
    </button>
    <h1 class="sub-title">{{ title }}</h1>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { PhArrowLeft } from '@phosphor-icons/vue'

defineProps<{ title: string }>()
const router = useRouter()
</script>

<style scoped>
.sub-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}

.back-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.back-btn:hover {
  background: var(--color-accent-soft);
}

.sub-title {
  font-family: var(--font-serif);
  font-size: 20px;
}
</style>
