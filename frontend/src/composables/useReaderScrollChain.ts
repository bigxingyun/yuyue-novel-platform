import { onUnmounted, ref, type Ref } from 'vue'
import { fetchChapter } from '@/api/books'
import { handleError } from '@/utils/errorHandler'
import type { ChapterBlock } from '@/types/chapterBlock'
import type { ChapterDetail } from '@/types/book'
import { resolveChapterBlocks } from '@/utils/resolveChapterBlocks'

export interface ScrollSection {
  chapterId: number
  title: string
  content: string
  blocks: ChapterBlock[]
  paragraphs: string[]
}

function sectionFromDetail(chapterId: number, detail: ChapterDetail): ScrollSection {
  const blocks = resolveChapterBlocks({
    content: detail.content,
    blocks: detail.blocks,
  })
  return {
    chapterId,
    title: detail.title,
    content: detail.content,
    blocks,
    paragraphs: detail.paragraphs,
  }
}

export function useReaderScrollChain(options: {
  enabled: Ref<boolean>
  chapterList: Ref<{ id: number; title: string }[]>
  scrollEl: Ref<HTMLElement | null>
  onChapterChange: (chapterId: number) => void
}) {
  const sections = ref<ScrollSection[]>([])
  const activeChapterId = ref(0)
  const loadingNext = ref(false)
  let scrollRaf = 0
  let syncing = false
  let loadGeneration = 0
  const inFlight = new Set<number>()

  function pushSection(chapterId: number, detail: ChapterDetail, generation: number) {
    if (generation !== loadGeneration) return false
    if (sections.value.some((s) => s.chapterId === chapterId)) return true
    sections.value.push(sectionFromDetail(chapterId, detail))
    return true
  }

  async function loadSection(
    chapterId: number,
    generation: number,
    options?: { prefetched?: ChapterDetail; silent?: boolean },
  ) {
    if (sections.value.some((s) => s.chapterId === chapterId)) return
    if (options?.prefetched) {
      pushSection(chapterId, options.prefetched, generation)
      return
    }
    if (inFlight.has(chapterId)) return
    inFlight.add(chapterId)
    try {
      const detail = await fetchChapter(chapterId)
      if (generation !== loadGeneration) return
      pushSection(chapterId, detail, generation)
    } catch (e) {
      if (generation === loadGeneration && !options?.silent) {
        handleError(e)
      }
      throw e
    } finally {
      inFlight.delete(chapterId)
    }
  }

  async function resetToChapter(chapterId: number, prefetched?: ChapterDetail): Promise<boolean> {
    syncing = true
    loadGeneration += 1
    const generation = loadGeneration
    sections.value = []
    activeChapterId.value = chapterId
    let ok = false
    try {
      if (prefetched) {
        ok = pushSection(chapterId, prefetched, generation)
      } else {
        await loadSection(chapterId, generation)
        ok = sections.value.some((s) => s.chapterId === chapterId)
      }
    } catch {
      ok = false
    } finally {
      syncing = false
    }
    return ok
  }

  async function tryAppendNext() {
    if (loadingNext.value || syncing || !options.enabled.value) return
    const last = sections.value[sections.value.length - 1]
    if (!last) return
    const idx = options.chapterList.value.findIndex((c) => c.id === last.chapterId)
    if (idx < 0 || idx >= options.chapterList.value.length - 1) return
    const nextId = options.chapterList.value[idx + 1].id
    if (sections.value.some((s) => s.chapterId === nextId)) return
    loadingNext.value = true
    const generation = loadGeneration
    try {
      await loadSection(nextId, generation, { silent: true })
    } catch {
      /* 续章失败时不阻断当前阅读 */
    } finally {
      loadingNext.value = false
    }
  }

  function updateActiveFromScroll() {
    const el = options.scrollEl.value
    if (!el) return
    const markerY = el.getBoundingClientRect().top + el.clientHeight * 0.32
    const nodes = el.querySelectorAll<HTMLElement>('.reader-chapter-section')
    let current = activeChapterId.value
    nodes.forEach((node) => {
      if (node.getBoundingClientRect().top <= markerY) {
        current = Number(node.dataset.chapterId)
      }
    })
    if (current && current !== activeChapterId.value) {
      activeChapterId.value = current
      options.onChapterChange(current)
    }
  }

  function onScroll() {
    if (!options.enabled.value) return
    cancelAnimationFrame(scrollRaf)
    scrollRaf = requestAnimationFrame(() => {
      const el = options.scrollEl.value
      if (!el) return
      updateActiveFromScroll()
      if (el.scrollTop + el.clientHeight >= el.scrollHeight - 180) {
        void tryAppendNext()
      }
    })
  }

  function calcChapterOffset(chapterId: number): number {
    const el = options.scrollEl.value
    if (!el) return 0
    const node = el.querySelector<HTMLElement>(`.reader-chapter-section[data-chapter-id="${chapterId}"]`)
    if (!node) {
      if (el.scrollHeight <= el.clientHeight) return 0
      return Math.min(1, Math.max(0, el.scrollTop / (el.scrollHeight - el.clientHeight)))
    }
    const height = node.offsetHeight
    if (height <= 0) return 0
    const sectionTop = getOffsetTopWithin(el, node)
    const scrolledInto = el.scrollTop + el.clientHeight * 0.25 - sectionTop
    return Math.min(1, Math.max(0, scrolledInto / height))
  }

  function getSectionContent(chapterId: number): string | undefined {
    return sections.value.find((s) => s.chapterId === chapterId)?.content
  }

  function updateSectionContent(chapterId: number, content: string) {
    const section = sections.value.find((s) => s.chapterId === chapterId)
    if (section) {
      section.content = content
      section.blocks = resolveChapterBlocks({ content })
      section.paragraphs = section.blocks
        .filter((b): b is Extract<ChapterBlock, { type: 'text' }> => b.type === 'text')
        .map((b) => b.text)
    }
  }

  function getOffsetTopWithin(container: HTMLElement, node: HTMLElement): number {
    let top = 0
    let el: HTMLElement | null = node
    while (el && el !== container) {
      top += el.offsetTop
      el = el.offsetParent as HTMLElement | null
    }
    return top
  }

  onUnmounted(() => {
    cancelAnimationFrame(scrollRaf)
  })

  return {
    sections,
    activeChapterId,
    loadingNext,
    resetToChapter,
    onScroll,
    calcChapterOffset,
    getSectionContent,
    updateSectionContent,
  }
}
