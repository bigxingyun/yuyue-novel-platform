<template>
  <Transition name="toast">
    <div v-if="visible" class="toast" :class="`toast-${type}`" role="status">
      {{ message }}
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { setNotify, type NotifyType } from '@/utils/errorHandler'

const visible = ref(false)
const message = ref('')
const type = ref<NotifyType>('error')
let timer: ReturnType<typeof setTimeout> | null = null

function show(msg: string, t: NotifyType = 'error') {
  message.value = msg
  type.value = t
  visible.value = true
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    visible.value = false
  }, 2800)
}

onMounted(() => setNotify(show))
onUnmounted(() => {
  if (timer) clearTimeout(timer)
})
</script>

<style scoped>
.toast {
  position: fixed;
  top: calc(16px + env(safe-area-inset-top, 0px));
  left: 50%;
  transform: translateX(-50%);
  z-index: 9000;
  padding: 12px 20px;
  border-radius: var(--radius-full);
  font-size: 14px;
  box-shadow: var(--shadow-lg);
  max-width: min(90vw, 360px);
  text-align: center;
}

.toast-error {
  background: var(--color-ink);
  color: #fff;
}

.toast-success {
  background: var(--color-success);
  color: #fff;
}

.toast-warning {
  background: var(--color-warning);
  color: #fff;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-8px);
}
</style>
