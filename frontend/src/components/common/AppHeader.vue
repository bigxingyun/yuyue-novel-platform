<template>
  <header class="app-header">
    <div class="app-header-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">阅</span>
        <span class="brand-name">欲阅</span>
      </RouterLink>

      <nav v-if="!isMobile" class="nav-desktop">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ active: isActive(item.to) }"
        >
          <component :is="item.icon" :size="18" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="header-actions">
        <template v-if="isLoggedIn">
          <RouterLink to="/profile" class="user-chip">
            <UserAvatar :src="userInfo?.avatar" :seed="userInfo?.id ?? 'yuyue'" size="xs" />
            <span class="user-meta">
              <span class="user-name">{{ userInfo?.nickname }}</span>
              <span v-if="userInfo?.title" class="user-title">{{ userInfo.title }}</span>
            </span>
          </RouterLink>
        </template>
        <template v-else>
          <RouterLink to="/auth/login" class="btn btn-ghost btn-sm">登录</RouterLink>
          <RouterLink to="/auth/register" class="btn btn-primary btn-sm">注册</RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { PhBooks, PhBookmark, PhUser } from '@phosphor-icons/vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { useUserStore } from '@/stores/user'
import { useDevice } from '@/composables/useDevice'

const route = useRoute()
const userStore = useUserStore()
const { isMobile } = useDevice()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)

const navItems = [
  { to: '/square', label: '广场', icon: PhBooks },
  { to: '/shelf', label: '书架', icon: PhBookmark },
  { to: '/profile', label: '我的', icon: PhUser },
]

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--header-height);
  background: color-mix(in srgb, var(--color-bg-elevated) 88%, transparent);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border-soft);
}

.app-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 20px;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: #fff;
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 700;
}

.brand-name {
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.nav-desktop {
  display: flex;
  gap: 4px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-full);
  font-size: 14px;
  color: var(--color-text-secondary);
  transition: background var(--transition), color var(--transition);
}

.nav-link:hover {
  color: var(--color-text);
  background: var(--color-accent-soft);
}

.nav-link.active {
  color: var(--color-accent);
  background: var(--color-accent-soft);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px 4px 4px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  transition: border-color var(--transition), box-shadow var(--transition);
}

.user-chip:hover {
  border-color: var(--color-accent-muted);
  box-shadow: var(--shadow-sm);
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.user-name {
  font-size: var(--text-sm);
  max-width: 96px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.user-title {
  font-size: 10px;
  color: var(--color-text-muted);
  max-width: 96px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 767px) {
  .user-meta {
    display: none;
  }
}
</style>
