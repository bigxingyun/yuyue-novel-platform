import { watch, onUnmounted } from 'vue'

/**
 * 打开浮层/侧栏时锁定背景滚动，防止「滑评论带动正文」
 */
export function useScrollLock(active: () => boolean) {
  let scrollY = 0

  function lock() {
    scrollY = window.scrollY
    document.body.style.position = 'fixed'
    document.body.style.top = `-${scrollY}px`
    document.body.style.left = '0'
    document.body.style.right = '0'
    document.body.style.overflow = 'hidden'
  }

  function unlock() {
    document.body.style.position = ''
    document.body.style.top = ''
    document.body.style.left = ''
    document.body.style.right = ''
    document.body.style.overflow = ''
    window.scrollTo(0, scrollY)
  }

  watch(
    active,
    (isActive) => {
      if (isActive) lock()
      else unlock()
    },
    { immediate: true },
  )

  onUnmounted(() => {
    if (active()) unlock()
  })
}
