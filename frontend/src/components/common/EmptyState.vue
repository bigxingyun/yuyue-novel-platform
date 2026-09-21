<template>
  <div class="empty-state">
    <div class="empty-icon">
      <component :is="icon" :size="40" weight="duotone" />
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="description" class="empty-desc">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  icon: Component
  title: string
  description?: string
}>()
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
  color: var(--color-text-secondary);
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-accent-soft);
  color: var(--color-accent);
  margin-bottom: 20px;
}

.empty-title {
  font-family: var(--font-serif);
  font-size: 18px;
  color: var(--color-text);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  max-width: 28ch;
  margin-bottom: 20px;
}
</style>
