/** 阅读页分页 — 左右滑动模式，基于 DOM 实测 */

import { computed, nextTick, onUnmounted, ref, watch, type ComputedRef, type Ref } from 'vue'
import {
  readerFontFamily,
  readerHorizontalPadding,
  readerLetterSpacing,
  type FontFamily,
  type LetterSpacing,
  type PageMargin,
} from './useReaderSettings'
import type { ChapterBlock } from '@/types/chapterBlock'
import { resolveMediaUrl } from '@/utils/mediaUrl'

export interface PaginationSettings {
  fontSize: number
  lineHeight: number
  fontFamily: FontFamily
  margin: PageMargin
  letterSpacing: LetterSpacing
}

/** 分页片段，保留原段落索引以支持段评 */
export interface PageSlice {
  text: string
  paraIndex: number
  isChapterComment?: boolean
  isImage?: boolean
  imageUrl?: string
  afterParagraphIndex?: number
}

export const CHAPTER_COMMENT_SLICE: PageSlice = {
  text: '',
  paraIndex: -1,
  isChapterComment: true,
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

export function useReaderPagination(
  blocks: ComputedRef<ChapterBlock[]>,
  viewportRef: Ref<HTMLElement | null>,
  settings: PaginationSettings,
  enabled: ComputedRef<boolean>,
) {
  const pages = ref<PageSlice[][]>([[]])
  const currentPage = ref(0)
  let observer: ResizeObserver | null = null
  let measureStyleEl: HTMLStyleElement | null = null

  function ensureMeasureStyle() {
    if (measureStyleEl) return
    measureStyleEl = document.createElement('style')
    measureStyleEl.textContent = `
      .yuyue-page-measure p {
        margin: 0 0 1.2em;
        text-indent: 2em;
        word-break: break-all;
      }
      .yuyue-chapter-comment-measure {
        margin: 1.8em 0 0.6em;
        padding: 14px 16px;
        min-height: 72px;
        border-radius: 8px;
        box-sizing: border-box;
      }
      .yuyue-image-measure {
        margin: 0.6em 0 1.4em;
        text-align: center;
      }
      .yuyue-image-measure img {
        display: block;
        width: 100%;
        max-height: 70vh;
        object-fit: contain;
      }
    `
    document.head.appendChild(measureStyleEl)
  }

  function createMeasurer(width: number): HTMLDivElement {
    ensureMeasureStyle()
    const horizontalPad = readerHorizontalPadding(settings.margin)
    const el = document.createElement('div')
    el.className = 'yuyue-page-measure'
    el.style.cssText = `
      position: fixed;
      left: -99999px;
      top: 0;
      visibility: hidden;
      overflow: hidden;
      width: ${width}px;
      box-sizing: border-box;
      padding: 0 calc(${horizontalPad} + 4px);
      font-family: ${readerFontFamily(settings.fontFamily)};
      font-size: ${settings.fontSize}px;
      line-height: ${settings.lineHeight};
      letter-spacing: ${readerLetterSpacing(settings.letterSpacing)};
    `
    document.body.appendChild(el)
    return el
  }

  function measureBlockHeight(measurer: HTMLDivElement, texts: string[]): number {
    if (!texts.length) return 0
    measurer.innerHTML = texts.map((p) => `<p>${escapeHtml(p)}</p>`).join('')
    return measurer.scrollHeight
  }

  function measureImageHeight(measurer: HTMLDivElement, url: string, maxHeight: number): number {
    const src = resolveMediaUrl(url)
    const cap = Math.floor(maxHeight * 0.7)
    measurer.innerHTML = `<div class="yuyue-image-measure"><img src="${escapeHtml(src)}" style="max-height:${cap}px" /></div>`
    const measured = measurer.scrollHeight || Math.floor(maxHeight * 0.45)
    return Math.min(measured, maxHeight)
  }

  function measureChapterCommentHeight(measurer: HTMLDivElement): number {
    measurer.innerHTML = '<div class="yuyue-chapter-comment-measure">章评</div>'
    return measurer.scrollHeight
  }

  function sliceHeight(measurer: HTMLDivElement, slice: PageSlice, pageHeight: number): number {
    if (slice.isChapterComment) return measureChapterCommentHeight(measurer)
    if (slice.isImage && slice.imageUrl) return measureImageHeight(measurer, slice.imageUrl, pageHeight)
    return measureBlockHeight(measurer, [slice.text])
  }

  function pageContentHeight(measurer: HTMLDivElement, slices: PageSlice[], pageHeight: number): number {
    let total = 0
    for (const slice of slices.filter((s) => !s.isChapterComment)) {
      total += sliceHeight(measurer, slice, pageHeight)
    }
    return total
  }

  function appendChapterCommentPage(
    measurer: HTMLDivElement,
    result: PageSlice[][],
    pageHeight: number,
  ) {
    if (!result.length) {
      result.push([{ ...CHAPTER_COMMENT_SLICE }])
      return
    }

    const commentHeight = measureChapterCommentHeight(measurer)
    const lastIdx = result.length - 1
    const lastPage = result[lastIdx].filter((s) => !s.isChapterComment)

    if (lastPage.length === 0) {
      result[lastIdx] = [{ ...CHAPTER_COMMENT_SLICE }]
      return
    }

    if (pageContentHeight(measurer, lastPage, pageHeight) + commentHeight <= pageHeight) {
      result[lastIdx] = [...lastPage, { ...CHAPTER_COMMENT_SLICE }]
      return
    }

    result.push([{ ...CHAPTER_COMMENT_SLICE }])
  }

  function splitLongParagraph(
    measurer: HTMLDivElement,
    para: string,
    paraIndex: number,
    maxHeight: number,
  ): PageSlice[] {
    if (measureBlockHeight(measurer, [para]) <= maxHeight) {
      return [{ text: para, paraIndex }]
    }

    const chunks: PageSlice[] = []
    let rest = para
    while (rest.length > 0) {
      let lo = 1
      let hi = rest.length
      let fit = 1
      while (lo <= hi) {
        const mid = Math.floor((lo + hi) / 2)
        const slice = rest.slice(0, mid)
        if (measureBlockHeight(measurer, [slice]) <= maxHeight) {
          fit = mid
          lo = mid + 1
        } else {
          hi = mid - 1
        }
      }
      if (fit <= 0) fit = 1
      chunks.push({ text: rest.slice(0, fit), paraIndex })
      rest = rest.slice(fit)
    }
    return chunks
  }

  function blocksToSlices(measurer: HTMLDivElement, chapterBlocks: ChapterBlock[], pageHeight: number): PageSlice[] {
    const flatSlices: PageSlice[] = []
    for (const block of chapterBlocks) {
      if (block.type === 'text') {
        flatSlices.push(...splitLongParagraph(measurer, block.text, block.paragraphIndex, pageHeight))
      } else {
        flatSlices.push({
          text: '',
          paraIndex: -1,
          isImage: true,
          imageUrl: block.url,
          afterParagraphIndex: block.afterParagraphIndex,
        })
      }
    }
    return flatSlices
  }

  function computePages() {
    const chapterBlocks = blocks.value
    if (!enabled.value) return

    if (!chapterBlocks.length) {
      pages.value = [[{ ...CHAPTER_COMMENT_SLICE }]]
      currentPage.value = 0
      return
    }

    const viewport = viewportRef.value
    if (!viewport) {
      pages.value = [
        chapterBlocks.flatMap((block) => {
          if (block.type === 'text') return [{ text: block.text, paraIndex: block.paragraphIndex }]
          return [{
            text: '',
            paraIndex: -1,
            isImage: true,
            imageUrl: block.url,
            afterParagraphIndex: block.afterParagraphIndex,
          }]
        }),
        [{ ...CHAPTER_COMMENT_SLICE }],
      ]
      return
    }

    const width = viewport.clientWidth
    const height = viewport.clientHeight
    if (width <= 0 || height <= 0) {
      pages.value = [
        chapterBlocks.flatMap((block) => {
          if (block.type === 'text') return [{ text: block.text, paraIndex: block.paragraphIndex }]
          return [{
            text: '',
            paraIndex: -1,
            isImage: true,
            imageUrl: block.url,
            afterParagraphIndex: block.afterParagraphIndex,
          }]
        }),
        [{ ...CHAPTER_COMMENT_SLICE }],
      ]
      return
    }

    const measurer = createMeasurer(width)
    try {
      const flatSlices = blocksToSlices(measurer, chapterBlocks, height)
      const result: PageSlice[][] = []
      let current: PageSlice[] = []

      for (const slice of flatSlices) {
        const candidate = [...current, slice]
        if (pageContentHeight(measurer, candidate, height) > height && current.length > 0) {
          result.push(current)
          current = [slice]
        } else {
          current = candidate
        }
      }
      if (current.length) result.push(current)

      appendChapterCommentPage(measurer, result.length ? result : [[]], height)

      const savedPage = currentPage.value
      pages.value = result.length ? result : [[{ ...CHAPTER_COMMENT_SLICE }]]
      if (savedPage >= pages.value.length) {
        currentPage.value = Math.max(0, pages.value.length - 1)
      }
    } finally {
      document.body.removeChild(measurer)
    }
  }

  function scheduleCompute() {
    nextTick(() => {
      requestAnimationFrame(() => computePages())
    })
  }

  function bindObserver(el: HTMLElement | null) {
    if (!observer) {
      observer = new ResizeObserver(() => {
        if (enabled.value) computePages()
      })
    }
    observer.disconnect()
    if (el) observer.observe(el)
  }

  watch(viewportRef, (el) => bindObserver(el), { immediate: true })

  watch(
    [
      blocks,
      () => settings.fontSize,
      () => settings.lineHeight,
      () => settings.fontFamily,
      () => settings.margin,
      () => settings.letterSpacing,
    ],
    () => {
      if (enabled.value) scheduleCompute()
    },
  )

  watch(enabled, (on) => {
    if (on) {
      currentPage.value = 0
      scheduleCompute()
    }
  })

  onUnmounted(() => {
    observer?.disconnect()
    measureStyleEl?.remove()
    measureStyleEl = null
  })

  const contentPageCount = computed(() => Math.max(1, pages.value.length))

  const pageProgress = computed(() => {
    if (pages.value.length <= 1) return 0
    const idx = Math.min(currentPage.value, pages.value.length - 1)
    return Math.round((idx / (pages.value.length - 1)) * 100)
  })

  function prevContentPage() {
    if (currentPage.value > 0) {
      currentPage.value -= 1
      return true
    }
    return false
  }

  function goToPage(index: number) {
    const clamped = Math.max(0, Math.min(index, pages.value.length - 1))
    currentPage.value = clamped
  }

  function resetPage() {
    currentPage.value = 0
    scheduleCompute()
  }

  return {
    pages,
    currentPage,
    contentPageCount,
    pageProgress,
    prevContentPage,
    goToPage,
    resetPage,
    scheduleCompute,
  }
}
