import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useDeviceStore } from '@/stores/device'
import type { DeviceType } from '@/types/enums'

const MOBILE_BREAKPOINT = 768

const isMobile = ref(false)
const deviceType = ref<DeviceType>('desktop')

function detectDeviceType(): DeviceType {
  const ua = navigator.userAgent
  if (/iPhone|iPad|iPod/i.test(ua)) return 'ios'
  if (/Android/i.test(ua)) return 'android'
  return 'desktop'
}

function update() {
  isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
  deviceType.value = detectDeviceType()
  try {
    useDeviceStore().deviceType = deviceType.value
  } catch {
    /* pinia not ready */
  }
}

export function useDevice() {
  onMounted(() => {
    update()
    window.addEventListener('resize', update)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', update)
  })

  const isIOS = computed(() => deviceType.value === 'ios')
  const isAndroid = computed(() => deviceType.value === 'android')
  const isDesktop = computed(() => deviceType.value === 'desktop')

  return { isMobile, deviceType, isIOS, isAndroid, isDesktop }
}

/** 模块级同步读取（无需在 setup 中调用 onMounted） */
export function getDeviceSnapshot() {
  return {
    isMobile: window.innerWidth < MOBILE_BREAKPOINT,
    deviceType: detectDeviceType(),
  }
}
