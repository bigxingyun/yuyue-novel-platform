/** 段落双击 / 双触检测（PC 双击、移动端连续双触） */

const TAP_INTERVAL_MS = 350
const TAP_MOVE_THRESHOLD_PX = 12

export function useParagraphTap(onActivate: (key: string) => void) {
  let lastTapAt = 0
  let lastTapKey = ''
  const touchStart = new Map<string, { x: number; y: number }>()

  function tryActivate(key: string) {
    const now = Date.now()
    if (key === lastTapKey && now - lastTapAt <= TAP_INTERVAL_MS) {
      onActivate(key)
      lastTapAt = 0
      lastTapKey = ''
      return
    }
    lastTapAt = now
    lastTapKey = key
  }

  function onDoubleClick(key: string) {
    onActivate(key)
  }

  function onTouchStart(key: string, e: TouchEvent) {
    const t = e.touches[0]
    if (!t) return
    touchStart.set(key, { x: t.clientX, y: t.clientY })
  }

  function onTouchEnd(key: string, e: TouchEvent) {
    const start = touchStart.get(key)
    touchStart.delete(key)
    if (!start) return

    const t = e.changedTouches[0]
    if (!t) return

    const dx = t.clientX - start.x
    const dy = t.clientY - start.y
    if (dx * dx + dy * dy > TAP_MOVE_THRESHOLD_PX * TAP_MOVE_THRESHOLD_PX) {
      lastTapKey = ''
      lastTapAt = 0
      return
    }

    tryActivate(key)
  }

  return { onDoubleClick, onTouchStart, onTouchEnd }
}

export function paragraphTapKey(chapterId: number, paraIndex: number) {
  return `${chapterId}:${paraIndex}`
}

export function parseParagraphTapKey(key: string): { chapterId: number; paraIndex: number } {
  const [chapterId, paraIndex] = key.split(':').map(Number)
  return { chapterId, paraIndex }
}
