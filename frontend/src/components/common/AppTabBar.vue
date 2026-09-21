<template>
  <nav class="tabbar">
    <RouterLink
      v-for="item in tabs"
      :key="item.to"
      :to="item.to"
      class="tabbar-item"
      :class="{ active: isActive(item.to) }"
    >
      <component :is="item.icon" :size="22" :weight="isActive(item.to) ? 'fill' : 'regular'" />
      <span>{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { PhBooks, PhBookmark, PhUser } from '@phosphor-icons/vue'

const route = useRoute()

const tabs = [
  { to: '/square', label: '广场', icon: PhBooks },
  { to: '/shelf', label: '书架', icon: PhBookmark },
  { to: '/profile', label: '我的', icon: PhUser },
]

function isActive(path: string) {
  if (path === '/profile') {
    return route.path.startsWith('/profile')
  }
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  height: calc(var(--tabbar-height) + var(--safe-bottom));
  padding-bottom: var(--safe-bottom);
  background: color-mix(in srgb, var(--color-bg-elevated) 92%, transparent);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--color-border-soft);
}

.tabbar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 11px;
  color: var(--color-text-muted);
  transition: color var(--transition);
}

.tabbar-item.active {
  color: var(--color-accent);
  font-weight: 500;
}
</style>
