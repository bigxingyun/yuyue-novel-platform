<template>
  <div class="sub-page page-container">
    <SubPageHeader :title="title" />
    <slot />
  </div>
</template>

<script setup lang="ts">
import SubPageHeader from '@/components/common/SubPageHeader.vue'

defineProps<{ title: string }>()
</script>
