import type { Router } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { notify } from '@/utils/errorHandler'

/** 仅本地开发调试时可设为 true；生产构建即使设为 true 也不跳过鉴权 */
const DEMO_MODE = import.meta.env.DEV && import.meta.env.VITE_DEMO_MODE === 'true'

const ROLE_LEVEL: Record<string, number> = {
  guest: 0,
  user: 1,
  author: 2,
  admin: 3,
  superadmin: 4,
}

const AUTH_ROUTE_NAMES = new Set(['login', 'register', 'recover'])

export function setupGuards(router: Router) {
  router.beforeEach(async (to, _from, next) => {
    if (DEMO_MODE) {
      return next()
    }

    const userStore = useUserStore()
    if (!userStore.bootstrapped) {
      await userStore.bootstrap()
    }

    const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
    if (requiresAuth && !userStore.isLoggedIn) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }

    const requiredRole = to.matched
      .map((r) => r.meta.role as string | undefined)
      .filter(Boolean)
      .pop()

    if (requiredRole && userStore.userInfo) {
      const userLevel = ROLE_LEVEL[userStore.userInfo.role] ?? 0
      const needLevel = ROLE_LEVEL[requiredRole] ?? 0
      if (userLevel < needLevel) {
        notify('无权访问该页面')
        return next({ name: 'square' })
      }
    }

    if (userStore.isLoggedIn && to.name && AUTH_ROUTE_NAMES.has(String(to.name))) {
      return next({ name: 'square' })
    }

    next()
  })
}
