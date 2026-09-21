import { onMounted, onUnmounted, ref, type Ref } from 'vue'

import { updateReadingProgress } from '@/api/reading'

import { enqueueProgress, flushProgressQueue } from '@/composables/useProgressQueue'



const REPORT_INTERVAL_MS = 3000



export function useReaderProgress(options: {

  bookId: Ref<number>

  chapterId: Ref<number>

  scrollEl: Ref<HTMLElement | null>

  enabled?: Ref<boolean>

  /** 翻页模式等自定义进度来源，返回 0–1 */

  getOffset?: () => number

}) {

  const chapterProgress = ref(0)

  let lastReportAt = 0

  let reportTimer: ReturnType<typeof setTimeout> | null = null



  function calcOffset(): number {

    if (options.getOffset) {

      return Math.min(1, Math.max(0, options.getOffset()))

    }

    const el = options.scrollEl.value

    if (!el || el.scrollHeight <= el.clientHeight) return 0

    return Math.min(1, Math.max(0, el.scrollTop / (el.scrollHeight - el.clientHeight)))

  }



  function updateLocalProgress() {

    chapterProgress.value = Math.round(calcOffset() * 100)

  }



  async function flushProgress(immediate = false) {

    if (options.enabled?.value === false) return

    const now = Date.now()

    if (!immediate && now - lastReportAt < REPORT_INTERVAL_MS) return

    lastReportAt = now

    updateLocalProgress()

    const payload = {

      bookId: options.bookId.value,

      chapterId: options.chapterId.value,

      offset: calcOffset(),

    }

    try {

      await updateReadingProgress(payload)

    } catch {

      enqueueProgress(payload)

    }

  }



  function scheduleReport() {

    updateLocalProgress()

    if (reportTimer) clearTimeout(reportTimer)

    reportTimer = setTimeout(() => flushProgress(true), REPORT_INTERVAL_MS)

  }



  function restoreScroll(offset: number) {

    const el = options.scrollEl.value

    if (!el || offset <= 0) return

    requestAnimationFrame(() => {

      const max = el.scrollHeight - el.clientHeight

      if (max > 0) el.scrollTop = offset * max

      updateLocalProgress()

    })

  }



  function restorePageIndex(contentPageCount: number, offset: number): number {

    if (contentPageCount <= 1) return 0

    return Math.min(contentPageCount - 1, Math.round(offset * (contentPageCount - 1)))

  }



  function onScroll() {

    scheduleReport()

  }



  onMounted(() => {

    flushProgressQueue()

    options.scrollEl.value?.addEventListener('scroll', onScroll, { passive: true })

  })



  onUnmounted(() => {

    options.scrollEl.value?.removeEventListener('scroll', onScroll)

    if (reportTimer) clearTimeout(reportTimer)

    flushProgress(true)

  })



  return { chapterProgress, flushProgress, restoreScroll, restorePageIndex, updateLocalProgress }

}

