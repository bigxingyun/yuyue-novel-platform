import router from '@/router'
import { useUserStore } from '@/stores/user'
import { clearToken } from '@/utils/token'

/** 清除本地会话（storage + Pinia），必要时跳转登录页 */
export function invalidateSession() {
  clearToken()
  const store = useUserStore()
  store.$patch({ token: null, userInfo: null })

  const route = router.currentRoute.value
  if (route.meta.requiresAuth && route.name !== 'login') {
    void router.push({ name: 'login', query: { redirect: route.fullPath } })
  }
}
