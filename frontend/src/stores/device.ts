import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DeviceType } from '@/types/enums'

export const useDeviceStore = defineStore('device', () => {
  const deviceType = ref<DeviceType>('desktop')
  return { deviceType }
})
