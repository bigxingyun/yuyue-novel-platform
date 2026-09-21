<template>
  <ErrorBoundary>
    <RouterView />
  </ErrorBoundary>
  <AppToast />
</template>

<script setup lang="ts">
import AppToast from '@/components/common/AppToast.vue'
import ErrorBoundary from '@/components/common/ErrorBoundary.vue'
</script>
