import { fetchReaderSettings, updateReaderSettings } from '@/api/profile'
import {
  normalizeReaderSettings,
  saveReaderSettings,
  type ReaderSettings,
} from '@/composables/useReaderSettings'
import { useUserStore } from '@/stores/user'

let syncTimer: ReturnType<typeof setTimeout> | null = null

/** 登录后从云端拉取阅读设置并覆盖本地 */
export async function pullReaderSettingsFromCloud(): Promise<ReaderSettings | null> {
  const userStore = useUserStore()
  if (!userStore.isLoggedIn) return null
  try {
    const result = await fetchReaderSettings()
    if (!result.settings) return null
    const merged = normalizeReaderSettings(result.settings as Partial<ReaderSettings>)
    saveReaderSettings(merged)
    return merged
  } catch {
    return null
  }
}

/** 本地保存并防抖上传云端 */
export function persistReaderSettings(settings: ReaderSettings) {
  saveReaderSettings(settings)
  const userStore = useUserStore()
  if (!userStore.isLoggedIn) return
  if (syncTimer) clearTimeout(syncTimer)
  syncTimer = setTimeout(async () => {
    if (!useUserStore().isLoggedIn) return
    try {
      await updateReaderSettings(settings)
    } catch {
      /* 静默失败，本地仍可用 */
    }
  }, 800)
}
