<template>
  <slot v-if="!hasError" />
  <div v-else class="error-boundary">
    <p class="error-title">页面出现问题</p>
    <p class="error-msg">{{ errorMessage }}</p>
    <button type="button" class="btn btn-primary btn-sm" @click="reset">重新加载</button>
  </div>
</template>

<script setup lang="ts">
import { onErrorCaptured, ref } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')

onErrorCaptured((err) => {
  hasError.value = true
  errorMessage.value = err instanceof Error ? err.message : '未知错误'
  return false
})

function reset() {
  hasError.value = false
  errorMessage.value = ''
  window.location.reload()
}
</script>

<style scoped>
.error-boundary {
  max-width: 480px;
  margin: 80px auto;
  padding: 24px;
  text-align: center;
}

.error-title {
  font-size: 18px;
  margin-bottom: 8px;
}

.error-msg {
  color: var(--color-text-muted);
  font-size: 14px;
  margin-bottom: 16px;
}
</style>
