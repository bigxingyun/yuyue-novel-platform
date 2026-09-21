<template>
  <div class="default-layout">
    <AppHeader />
    <main class="main-content" :class="{ 'has-tabbar': isMobile }">
      <RouterView v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    <AppTabBar v-if="isMobile" />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/common/AppHeader.vue'
import AppTabBar from '@/components/common/AppTabBar.vue'
import { useDevice } from '@/composables/useDevice'

const { isMobile } = useDevice()
</script>

<style scoped>
.default-layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

.main-content.has-tabbar {
  padding-bottom: calc(var(--tabbar-height) + var(--safe-bottom));
}
</style>
