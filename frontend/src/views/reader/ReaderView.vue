<template>
  <div
    class="reader"
    :class="[
      settings.useCustomBg ? 'theme-custom' : `theme-${settings.theme}`,
      { 'toolbar-visible': toolbarVisible },
    ]"
    :style="readerSurfaceStyle"
    @click="onReaderClick"
  >
    <header class="reader-toolbar" :class="{ 'toolbar-editing': authorEditMode }" @click.stop>
      <button class="toolbar-btn" @click="router.back()">
        <PhArrowLeft :size="20" />
      </button>
      <div class="toolbar-title">
        <span v-if="authorEditMode" class="toolbar-edit-badge">编辑中</span>
        <span class="toolbar-book">{{ bookTitle }}</span>
        <span class="toolbar-chapter">{{ currentChapter?.title }}</span>
      </div>
      <button
        v-if="isAuthorMode && !authorEditMode"
        class="toolbar-btn"
        title="编辑正文"
        @click="authorEditMode = true"
      >
        <PhPencilSimple :size="20" />
      </button>
      <button
        v-if="authorEditMode"
        class="toolbar-btn toolbar-done-btn"
        @click="authorEditMode = false"
      >
        完成
      </button>
      <button v-if="!authorEditMode" class="toolbar-btn" @click="panelOpen = true">
        <PhList :size="20" />
      </button>
    </header>

    <div
      ref="scrollZoneRef"
      class="reader-scroll-zone"
      :class="{
        'scroll-locked': paraPanelOpen || panelOpen,
        'page-mode': isPageMode && !authorEditMode,
      }"
      @scroll.passive="onScrollZoneScroll"
      @touchstart.passive="onTouchStart"
      @touchend="onTouchEnd"
    >
      <!-- 滚动模式，或作者编辑模式（翻页时也用块编辑） -->
      <template v-if="!isPageMode || authorEditMode">
        <article class="reader-content">
          <template v-if="authorEditMode">
            <AuthorChapterContentEditor
              :blocks="chapterBlocks"
              @insert-image="onInsertImage"
              @remove-image="onRemoveImage"
              @replace-image="onReplaceImage"
            />
          </template>
          <template v-else>
          <section
            v-for="section in displaySections"
            :key="section.chapterId"
            class="reader-chapter-section"
            :data-chapter-id="section.chapterId"
          >
            <h2 v-if="(book?.chapters.length ?? 0) > 1" class="reader-chapter-heading">
              {{ section.title }}
            </h2>
            <ReaderChapterContent
              :blocks="section.blocks"
              :chapter-id="section.chapterId"
              :para-comment-count="paraCommentCount"
              @para-dbl-click="onParaDblClick"
              @para-touch-start="onParaTouchStart"
              @para-touch-end="onParaTouchEnd"
              @open-para-comment="openParaComment"
            />
            <ReaderChapterCommentCard
              :featured="featuredChapterComment(section.chapterId)"
              :count="getChapterComments(section.chapterId).length"
              @open="openChapterComment(section.chapterId, featuredChapterComment(section.chapterId) ? 'view' : 'compose')"
            />
          </section>
          <p v-if="loadingNextChapter" class="scroll-loading-hint">加载下一章…</p>
          </template>
        </article>
      </template>

      <!-- 翻页模式（非编辑态） -->
      <template v-else>
        <div ref="pageViewportRef" class="page-viewport">
          <div
            class="page-tap-left"
            aria-label="上一页"
            @click.stop="handlePrevPage"
          />
          <div
            class="page-tap-right"
            aria-label="下一页"
            @click.stop="handleNextPage"
          />
          <Transition mode="out-in" :name="pageTransitionName">
            <div :key="currentPage" class="page-sheet">
              <article class="reader-content reader-page-content">
              <ReaderPageContent
                :slices="currentPageSlices"
                :chapter-id="chapterId"
                :para-comment-count="paraCommentCount"
                :featured-chapter-comment="featuredChapterComment(chapterId)"
                :chapter-comment-count="getChapterComments(chapterId).length"
                :chapter-comment-mode="featuredChapterComment(chapterId) ? 'view' : 'compose'"
                @para-dbl-click="onParaDblClick"
                @para-touch-start="onParaTouchStart"
                @para-touch-end="onParaTouchEnd"
                @open-para-comment="openParaComment"
                @open-chapter-comment="openChapterComment(chapterId, $event)"
                @image-loaded="scheduleCompute"
              />
              </article>
            </div>
          </Transition>
        </div>
        <div class="page-indicator">
          {{ currentPage + 1 }} / {{ contentPageCount }}
        </div>
      </template>
    </div>

    <!-- 二级菜单面板 -->
    <Transition name="reader-panel">
      <div v-if="panelOpen" class="reader-panel-overlay" @click="panelOpen = false">
        <div class="reader-panel" @click.stop>
          <div class="panel-tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              class="panel-tab"
              :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>

          <div v-if="activeTab === 'toc'" class="panel-body">
            <button
              v-for="ch in book?.chapters"
              :key="ch.id"
              class="toc-item"
              :class="{ active: ch.id === currentChapter?.id }"
              @click="switchChapter(ch.id)"
            >
              {{ ch.title }}
            </button>
          </div>

          <div v-else-if="activeTab === 'progress'" class="panel-body">
            <p class="progress-label">全书进度</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${bookProgress}%` }" />
            </div>
            <p class="progress-hint">全书 {{ bookProgress }}%</p>
            <p class="progress-label">当前章节</p>
            <p class="progress-chapter">{{ currentChapter?.title }}</p>
            <p class="progress-label">本章进度</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: `${displayProgress}%` }" />
            </div>
            <p class="progress-hint">本章 {{ displayProgress }}%</p>
          </div>

          <div v-else class="panel-body settings">
            <label class="setting-row">
              <span>字号</span>
              <input v-model.number="settings.fontSize" type="range" min="14" max="24" />
              <span class="setting-val">{{ settings.fontSize }}px</span>
            </label>
            <label class="setting-row">
              <span>段间距</span>
              <input v-model.number="settings.lineHeight" type="range" min="1.6" max="2.4" step="0.1" />
            </label>
            <p class="progress-label">字间距</p>
            <div class="mode-group">
              <button
                v-for="s in letterSpacingOptions"
                :key="s.id"
                class="mode-btn"
                :class="{ active: settings.letterSpacing === s.id }"
                @click="settings.letterSpacing = s.id"
              >
                {{ s.label }}
              </button>
            </div>
            <p class="progress-label">字体颜色</p>
            <div class="mode-group">
              <button
                v-for="c in textColorOptions"
                :key="c.id"
                class="mode-btn"
                :class="{ active: settings.textColor === c.id }"
                @click="settings.textColor = c.id"
              >
                {{ c.label }}
              </button>
            </div>
            <label v-if="settings.textColor === 'custom'" class="setting-row">
              <span>自定义色</span>
              <input v-model="settings.customTextColor" type="color" class="color-input" />
            </label>
            <p class="progress-label">背景</p>
            <div class="theme-group">
              <button
                v-for="t in themes"
                :key="t.id"
                class="theme-btn"
                :class="{ active: !settings.useCustomBg && settings.theme === t.id }"
                :style="{ background: t.bg }"
                @click="selectTheme(t.id)"
              />
            </div>
            <label class="setting-row custom-bg-row">
              <span>自定义背景</span>
              <input v-model="settings.useCustomBg" type="checkbox" />
              <input
                v-if="settings.useCustomBg"
                v-model="settings.customBgColor"
                type="color"
                class="color-input"
              />
            </label>
            <p class="progress-label">字体</p>
            <div class="mode-group">
              <button
                v-for="f in fontOptions"
                :key="f.id"
                class="mode-btn"
                :class="{ active: settings.fontFamily === f.id }"
                @click="settings.fontFamily = f.id"
              >
                {{ f.label }}
              </button>
            </div>
            <p class="progress-label">页边距</p>
            <div class="mode-group">
              <button
                v-for="m in marginOptions"
                :key="m.id"
                class="mode-btn"
                :class="{ active: settings.margin === m.id }"
                @click="settings.margin = m.id"
              >
                {{ m.label }}
              </button>
            </div>
            <p class="progress-label">翻页模式</p>
            <div v-if="!isDesktop" class="mode-group">
              <button
                v-for="m in modes"
                :key="m.id"
                class="mode-btn"
                :class="{ active: settings.pageMode === m.id }"
                @click="settings.pageMode = m.id"
              >
                {{ m.label }}
              </button>
            </div>
            <p v-else class="setting-hint">PC 端固定为上下滚动，不可更改</p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 段评侧栏：独立滚动，锁定正文 -->
    <Transition name="para-overlay">
      <div v-if="paraPanelOpen" class="para-panel-overlay" @click="closeParaPanel">
        <aside class="para-panel" @click.stop>
          <header class="para-panel-head">
            <span>段评</span>
            <button type="button" aria-label="关闭" @click="closeParaPanel">
              <PhX :size="20" />
            </button>
          </header>
          <p class="para-preview">{{ paragraphs[activeParaIndex] }}</p>
          <div class="para-panel-scroll">
            <div v-if="activeParaComments.length" class="para-comments">
              <CommentItem
                v-for="c in activeParaComments"
                :key="c.id"
                :comment="c"
                type="paragraph"
                :can-pin="canPinComments"
                :replying-to="replyingTo"
                @reply="replyingTo = $event"
                @pin="onPinParagraph"
                @delete="onDeleteParagraph"
                @submit-reply="onSubmitParagraphReply"
                @cancel-reply="replyingTo = null"
              />
            </div>
            <p v-else class="para-empty-hint">暂无段评，写下第一条吧</p>
          </div>
          <footer class="para-panel-compose">
            <textarea
              ref="paraCommentInput"
              v-model="newParaComment"
              class="field-input"
              placeholder="写下你的想法…"
              rows="3"
            />
            <button class="btn btn-primary btn-sm btn-block" @click="submitParaComment">
              发表段评
            </button>
          </footer>
        </aside>
      </div>
    </Transition>

    <!-- 章评侧栏 -->
    <Transition name="para-overlay">
      <div v-if="chapterPanelOpen" class="para-panel-overlay" @click="closeChapterPanel">
        <aside class="para-panel chapter-panel" @click.stop>
          <header class="para-panel-head">
            <span>章评</span>
            <button type="button" aria-label="关闭" @click="closeChapterPanel">
              <PhX :size="20" />
            </button>
          </header>
          <p class="para-preview chapter-panel-sub">{{ activeChapterPanelTitle }}</p>
          <div class="para-panel-scroll">
            <div v-if="activeChapterPanelComments.length" class="para-comments">
              <CommentItem
                v-for="c in activeChapterPanelComments"
                :key="c.id"
                :comment="c"
                type="chapter"
                :can-pin="canPinComments"
                :replying-to="replyingTo"
                @reply="replyingTo = $event"
                @pin="onPinChapter"
                @delete="onDeleteChapter"
                @submit-reply="onSubmitChapterReply"
                @cancel-reply="replyingTo = null"
              />
            </div>
            <p v-else class="para-empty-hint">暂无章评，写下第一条吧</p>
          </div>
          <footer class="para-panel-compose">
            <textarea
              ref="chapterCommentInput"
              v-model="newChapterComment"
              class="field-input"
              placeholder="写下你的章评…"
              rows="3"
            />
            <button class="btn btn-primary btn-sm btn-block" @click="submitChapterComment">
              发表章评
            </button>
          </footer>
        </aside>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PhArrowLeft, PhChatCircle, PhList, PhPencilSimple, PhX } from '@phosphor-icons/vue'
import CommentItem from '@/components/comment/CommentItem.vue'
import AuthorChapterContentEditor from '@/components/reader/AuthorChapterContentEditor.vue'
import ReaderChapterCommentCard from '@/components/reader/ReaderChapterCommentCard.vue'
import ReaderChapterContent from '@/components/reader/ReaderChapterContent.vue'
import ReaderPageContent from '@/components/reader/ReaderPageContent.vue'
import { fetchBookDetail, fetchChapter } from '@/api/books'
import { updateAuthorChapter } from '@/api/author'
import { uploadImageForContent } from '@/api/upload'
import { useChapterComments } from '@/composables/useChapterComments'
import { pickFeaturedChapterComment } from '@/utils/chapterCommentFeatured'
import { useParagraphTap, paragraphTapKey, parseParagraphTapKey } from '@/composables/useParagraphTap'
import { useReaderProgress } from '@/composables/useReader'
import { loadReaderSettings } from '@/composables/useReaderSettings'
import { persistReaderSettings, pullReaderSettingsFromCloud } from '@/composables/useReaderSettingsSync'
import {
  readerBackground,
  readerFontFamily,
  readerHorizontalPadding,
  readerLetterSpacing,
  readerTextColor,
  type FontFamily,
  type LetterSpacing,
  type PageMargin,
  type ReaderTheme,
  type TextColorPreset,
} from '@/composables/useReaderSettings'
import { useReaderScrollChain } from '@/composables/useReaderScrollChain'
import { useReaderPagination } from '@/composables/useReaderPagination'
import { useScrollLock } from '@/composables/useScrollLock'
import { useUserStore } from '@/stores/user'
import type { BookDetail } from '@/types/book'
import type { ChapterDetail } from '@/types/book'
import type { CommentItem as CommentItemType } from '@/types/comment'
import { handleError, notify } from '@/utils/errorHandler'
import { insertImageAfterParagraph, removeImageAt } from '@/utils/parseChapterBlocks'
import { resolveChapterBlocks } from '@/utils/resolveChapterBlocks'
import { firstMeaningfulContent } from '@/utils/firstMeaningful'

const DESKTOP_MQ = '(min-width: 768px)'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const authorEditMode = ref(false)
const imageSaving = ref(false)
const toolbarVisible = ref(true)

watch(authorEditMode, (editing) => {
  if (editing) toolbarVisible.value = true
})
const panelOpen = ref(false)
const paraPanelOpen = ref(false)
const chapterPanelOpen = ref(false)
const activeChapterPanelId = ref(0)
const activeTab = ref<'toc' | 'progress' | 'settings'>('toc')
const activeParaIndex = ref(0)
const newParaComment = ref('')
const newChapterComment = ref('')
const paraCommentInput = ref<HTMLTextAreaElement | null>(null)
const chapterCommentInput = ref<HTMLTextAreaElement | null>(null)
const isDesktop = ref(false)
const scrollZoneRef = ref<HTMLElement | null>(null)
const pageViewportRef = ref<HTMLElement | null>(null)
const pageProgressRestored = ref(false)
const pendingChapterCommentFocus = ref(false)
const scrollChainNavigating = ref(false)
const pageTurnDirection = ref<'forward' | 'backward'>('forward')
const pendingPageOnChapterLoad = ref<'first' | 'last' | null>(null)
let loadReaderSeq = 0

function getAuthorChapterContent(): string {
  const cid = chapterId.value
  return firstMeaningfulContent(getSectionContent(cid), chapter.value?.content)
}

useScrollLock(() => paraPanelOpen.value || chapterPanelOpen.value || panelOpen.value)

const book = ref<BookDetail | null>(null)
const chapter = ref<ChapterDetail | null>(null)
const loading = ref(true)

const settings = reactive(loadReaderSettings())

watch(
  settings,
  () => persistReaderSettings({ ...settings }),
  { deep: true },
)

const bookId = computed(() => Number(route.params.bookId))
const chapterId = computed(() => Number(route.params.chapterId))
const chapterList = computed(() => book.value?.chapters ?? [])

const isPageMode = computed(
  () => !isDesktop.value && settings.pageMode !== 'scroll',
)

const {
  sections: scrollSections,
  activeChapterId,
  loadingNext: loadingNextChapter,
  resetToChapter,
  onScroll: onScrollChain,
  calcChapterOffset,
  getSectionContent,
  updateSectionContent,
} = useReaderScrollChain({
  enabled: computed(() => !isPageMode.value),
  chapterList,
  scrollEl: scrollZoneRef,
  onChapterChange: (id) => {
    void onScrollChapterChange(id)
  },
})

const progressChapterId = computed(() =>
  !isPageMode.value ? activeChapterId.value || chapterId.value : chapterId.value,
)

const {
  getChapterComments,
  getParaComments,
  paraCommentCount,
  replyingTo,
  loadComments,
  prefetchComments,
  submitChapter,
  submitParagraph,
  removeComment,
  pinCommentItem,
} = useChapterComments(() => progressChapterId.value)

const canPinComments = computed(
  () => !!userStore.userInfo && book.value?.authorId === userStore.userInfo.id,
)

const tabs = [
  { id: 'toc' as const, label: '目录' },
  { id: 'progress' as const, label: '进度' },
  { id: 'settings' as const, label: '设置' },
]

const modes = [
  { id: 'scroll' as const, label: '上下滚动' },
  { id: 'slide' as const, label: '左右滑动' },
]

const themes: { id: ReaderTheme; bg: string }[] = [
  { id: 'paper', bg: '#f7f6f2' },
  { id: 'green', bg: '#e8efe4' },
  { id: 'night', bg: '#1a1d24' },
]

const fontOptions: { id: FontFamily; label: string }[] = [
  { id: 'serif', label: '宋意 serif' },
  { id: 'sans', label: '黑体 sans' },
  { id: 'kai', label: '楷体' },
  { id: 'song', label: '宋体' },
]

const marginOptions: { id: PageMargin; label: string }[] = [
  { id: 'narrow', label: '窄' },
  { id: 'medium', label: '中' },
  { id: 'wide', label: '宽' },
]

const letterSpacingOptions: { id: LetterSpacing; label: string }[] = [
  { id: 'tight', label: '紧凑' },
  { id: 'normal', label: '标准' },
  { id: 'wide', label: '宽松' },
]

const textColorOptions: { id: TextColorPreset; label: string }[] = [
  { id: 'default', label: '默认' },
  { id: 'dark', label: '深黑' },
  { id: 'brown', label: '棕褐' },
  { id: 'gray', label: '灰' },
  { id: 'custom', label: '自定义' },
]

function selectTheme(theme: ReaderTheme) {
  settings.useCustomBg = false
  settings.theme = theme
}

const bookTitle = computed(() => book.value?.title ?? '')
const currentChapter = computed(
  () => book.value?.chapters.find((c) => c.id === progressChapterId.value),
)

const paragraphs = computed(() => chapter.value?.paragraphs ?? [])

const chapterBlocks = computed(() =>
  resolveChapterBlocks({
    content: chapter.value?.content,
    blocks: chapter.value?.blocks,
  }),
)

const displaySections = computed(() => {
  if (scrollSections.value.length > 0) return scrollSections.value
  if (!chapter.value) return []
  return [
    {
      chapterId: chapter.value.id,
      title: chapter.value.title,
      content: chapter.value.content,
      blocks: chapterBlocks.value,
      paragraphs: chapter.value.paragraphs,
    },
  ]
})

const isAuthorMode = computed(
  () => !!book.value && !!userStore.userInfo && book.value.authorId === userStore.userInfo.id,
)

const {
  pages,
  currentPage,
  contentPageCount,
  pageProgress,
  prevContentPage,
  resetPage,
  scheduleCompute,
} = useReaderPagination(chapterBlocks, pageViewportRef, settings, isPageMode)

const { chapterProgress, restoreScroll, restorePageIndex, flushProgress, updateLocalProgress } =
  useReaderProgress({
    bookId,
    chapterId: progressChapterId,
    scrollEl: scrollZoneRef,
    getOffset: () => {
      if (authorEditMode.value || !isPageMode.value) {
        return calcChapterOffset(activeChapterId.value || chapterId.value)
      }
      const total = contentPageCount.value
      if (total <= 0) return 0
      return total <= 1 ? 0 : currentPage.value / (total - 1)
    },
  })

const pageTransitionName = computed(() => {
  const dir = pageTurnDirection.value === 'forward' ? 'fwd' : 'back'
  return `page-slide-${dir}`
})

const currentPageSlices = computed(() => pages.value[currentPage.value] ?? [])

const displayProgress = computed(() => {
  if (!isPageMode.value) return chapterProgress.value
  return pageProgress.value
})

const bookProgress = computed(() => {
  const b = book.value
  const ch = currentChapter.value
  if (!b || !ch || b.wordCount <= 0) return 0
  const chapters = b.chapters
  const idx = chapters.findIndex((c) => c.id === ch.id)
  let readWords = 0
  for (let i = 0; i < idx; i++) readWords += chapters[i]?.wordCount ?? 0
  readWords += (displayProgress.value / 100) * ch.wordCount
  return Math.min(100, Math.round((readWords / b.wordCount) * 100))
})

const readerStyles = computed(() => ({
  fontSize: `${settings.fontSize}px`,
  lineHeight: String(settings.lineHeight),
  fontFamily: readerFontFamily(settings.fontFamily),
  letterSpacing: readerLetterSpacing(settings.letterSpacing),
  '--reader-padding-x': readerHorizontalPadding(settings.margin),
}))

const readerSurfaceStyle = computed(() => {
  const style: Record<string, string> = { ...readerStyles.value }
  const bg = readerBackground(settings)
  if (bg) style.background = bg
  const color = readerTextColor(settings)
  if (color) style.color = color
  return style
})

const activeParaComments = computed(
  () => getParaComments(progressChapterId.value, activeParaIndex.value),
)

const activeChapterPanelComments = computed(() =>
  getChapterComments(activeChapterPanelId.value),
)

const activeChapterPanelTitle = computed(
  () => book.value?.chapters.find((c) => c.id === activeChapterPanelId.value)?.title ?? '',
)

function featuredChapterComment(chId: number) {
  return pickFeaturedChapterComment(getChapterComments(chId), book.value?.authorId ?? 0)
}

const {
  onDoubleClick: onParaDblClickBase,
  onTouchStart: onParaTouchStartBase,
  onTouchEnd: onParaTouchEndBase,
} = useParagraphTap((key) => {
  const { chapterId: chId, paraIndex } = parseParagraphTapKey(key)
  openParaComment(chId, paraIndex, 'compose')
})

function onParaDblClick(chId: number, paraIndex: number) {
  if (authorEditMode.value) return
  onParaDblClickBase(paragraphTapKey(chId, paraIndex))
}

function onParaTouchStart(chId: number, paraIndex: number, e: TouchEvent) {
  if (authorEditMode.value) return
  onParaTouchStartBase(paragraphTapKey(chId, paraIndex), e)
}

function onParaTouchEnd(chId: number, paraIndex: number, e: TouchEvent) {
  if (authorEditMode.value) return
  onParaTouchEndBase(paragraphTapKey(chId, paraIndex), e)
}

let hideTimer: ReturnType<typeof setTimeout> | null = null
let desktopMq: MediaQueryList | null = null

function syncDesktopMode() {
  isDesktop.value = desktopMq?.matches ?? false
}

function onDesktopMqChange() {
  syncDesktopMode()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    if (chapterPanelOpen.value) closeChapterPanel()
    else if (paraPanelOpen.value) closeParaPanel()
    else if (panelOpen.value) panelOpen.value = false
    return
  }
  if (!isPageMode.value || authorEditMode.value || panelOpen.value || paraPanelOpen.value || chapterPanelOpen.value) return
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    e.preventDefault()
    handleNextPage()
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault()
    handlePrevPage()
  }
}

let touchStartX = 0
let touchStartY = 0

function onTouchStart(e: TouchEvent) {
  if (!isPageMode.value || authorEditMode.value || panelOpen.value || paraPanelOpen.value || chapterPanelOpen.value) return
  touchStartX = e.touches[0]?.clientX ?? 0
  touchStartY = e.touches[0]?.clientY ?? 0
}

function onTouchEnd(e: TouchEvent) {
  if (!isPageMode.value || authorEditMode.value || panelOpen.value || paraPanelOpen.value || chapterPanelOpen.value) return
  const dx = (e.changedTouches[0]?.clientX ?? 0) - touchStartX
  const dy = (e.changedTouches[0]?.clientY ?? 0) - touchStartY
  if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy)) return
  if (dx < 0) handleNextPage()
  else handlePrevPage()
}

async function loadReader() {
  const bid = Number(route.params.bookId)
  const cid = Number(route.params.chapterId)
  const seq = ++loadReaderSeq

  if (scrollChainNavigating.value) {
    scrollChainNavigating.value = false
    activeChapterId.value = cid
    updateChapterMeta(cid)
    await loadComments(cid)
    return
  }

  loading.value = true
  pageProgressRestored.value = false
  try {
    const [bookDetail, chapterDetail] = await Promise.all([
      fetchBookDetail(bid),
      fetchChapter(cid),
    ])
    if (seq !== loadReaderSeq) return
    book.value = bookDetail
    chapter.value = chapterDetail
    activeChapterId.value = cid

    if (!isPageMode.value) {
      const ok = await resetToChapter(cid, chapterDetail)
      if (seq !== loadReaderSeq) return
      if (!ok) {
        notify('章节正文加载失败')
      }
      await loadComments(cid)
      const prog = bookDetail.progress
      if (prog && prog.chapterId === cid && prog.offset > 0) {
        restoreScroll(prog.offset)
      } else {
        restoreScroll(0)
      }
    } else {
      await loadComments(cid)
    }
  } catch (e) {
    if (seq !== loadReaderSeq) return
    handleError(e)
    book.value = null
    chapter.value = null
  } finally {
    if (seq !== loadReaderSeq) return
    loading.value = false
    if (isPageMode.value) {
      resetPage()
      scheduleCompute()
    }
    if (route.query.focus === 'chapter-comment') {
      pendingChapterCommentFocus.value = true
      const query = { ...route.query }
      delete query.focus
      router.replace({ path: route.path, query })
    }
  }
}

watch(
  () =>
    [
      pendingChapterCommentFocus.value,
      loading.value,
      isPageMode.value,
      pages.value,
    ] as const,
  ([pending, isLoading, pageMode, pageList]) => {
    if (!pending || isLoading) return
    if (pageMode && chapterBlocks.value.length > 0 && !pageList.some((p) => p.length > 0)) return
    tryFocusChapterCommentInput()
  },
  { deep: true },
)

function tryFocusChapterCommentInput() {
  if (!pendingChapterCommentFocus.value) return
  if (isPageMode.value && chapterBlocks.value.length > 0 && !pages.value.some((p) => p.length > 0)) {
    return
  }
  pendingChapterCommentFocus.value = false
  focusChapterCommentInput()
}

watch(isPageMode, async (pageMode, prev) => {
  if (prev === undefined) return
  if (pageMode) {
    pageProgressRestored.value = false
    resetPage()
    scheduleCompute()
  } else if (chapterId.value && chapter.value) {
    const ok = await resetToChapter(chapterId.value, chapter.value)
    if (!ok) notify('章节正文加载失败')
    await loadComments(chapterId.value)
  }
})

watch(chapterId, () => {
  if (pendingPageOnChapterLoad.value !== 'last') {
    currentPage.value = 0
  }
  pageProgressRestored.value = false
})

watch([pages, pendingPageOnChapterLoad, () => book.value?.progress], () => {
  if (
    pendingPageOnChapterLoad.value === 'last' &&
    isPageMode.value &&
    pages.value.length > 0
  ) {
    currentPage.value = pages.value.length - 1
    pendingPageOnChapterLoad.value = null
    pageProgressRestored.value = true
    updateLocalProgress()
    return
  }
  if (pageProgressRestored.value || !isPageMode.value || contentPageCount.value <= 0) return
  const prog = book.value?.progress
  if (prog && prog.chapterId === chapterId.value) {
    currentPage.value = restorePageIndex(contentPageCount.value, prog.offset)
    pageProgressRestored.value = true
    updateLocalProgress()
  }
})

watch(currentPage, () => {
  if (isPageMode.value) {
    updateLocalProgress()
    flushProgress()
  }
})

watch(pageViewportRef, (el) => {
  if (el && isPageMode.value) scheduleCompute()
})

function goNextChapter() {
  const chapters = book.value?.chapters ?? []
  const idx = chapters.findIndex((c) => c.id === chapterId.value)
  if (idx >= 0 && idx < chapters.length - 1) {
    switchChapter(chapters[idx + 1].id)
  }
}

watch(
  scrollSections,
  (sections) => {
    for (const section of sections) {
      void prefetchComments(section.chapterId)
    }
  },
  { deep: true },
)

watch(
  () => [route.params.bookId, route.params.chapterId],
  () => loadReader(),
)

onMounted(async () => {
  const cloud = await pullReaderSettingsFromCloud()
  if (cloud) Object.assign(settings, cloud)
  loadReader()
  desktopMq = window.matchMedia(DESKTOP_MQ)
  syncDesktopMode()
  desktopMq.addEventListener('change', onDesktopMqChange)
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  desktopMq?.removeEventListener('change', onDesktopMqChange)
  window.removeEventListener('keydown', onKeydown)
  if (hideTimer) clearTimeout(hideTimer)
})

function onReaderClick() {
  toolbarVisible.value = !toolbarVisible.value
  if (hideTimer) clearTimeout(hideTimer)
  if (toolbarVisible.value) {
    hideTimer = setTimeout(() => {
      toolbarVisible.value = false
    }, 3000)
  }
}

function onScrollZoneScroll() {
  if (!isPageMode.value) onScrollChain()
}

function updateChapterMeta(id: number) {
  const section = scrollSections.value.find((s) => s.chapterId === id)
  const meta = book.value?.chapters.find((c) => c.id === id)
  if (chapter.value && meta) {
    chapter.value = {
      ...chapter.value,
      id,
      title: meta.title,
      content: firstMeaningfulContent(section?.content, chapter.value.content),
      paragraphs:
        section?.paragraphs?.length ? section.paragraphs : chapter.value.paragraphs,
      blocks: section?.blocks?.length ? section.blocks : chapter.value.blocks,
    }
  }
}

async function refreshChapterContent(chapterIdToRefresh: number) {
  const detail = await fetchChapter(chapterIdToRefresh)
  const blocks = resolveChapterBlocks({
    content: detail.content,
    blocks: detail.blocks,
  })
  if (chapter.value?.id === chapterIdToRefresh) {
    chapter.value = { ...detail, blocks }
  }
  const section = scrollSections.value.find((s) => s.chapterId === chapterIdToRefresh)
  if (section) {
    section.content = detail.content
    section.blocks = blocks
    section.paragraphs = detail.paragraphs
  }
  if (isPageMode.value) scheduleCompute()
}

async function saveChapterContent(newContent: string) {
  const cid = chapterId.value
  await updateAuthorChapter(cid, { content: newContent })
  updateSectionContent(cid, newContent)
  await refreshChapterContent(cid)
}

async function onInsertImage(paragraphIndex: number) {
  if (!isAuthorMode.value || !chapter.value || imageSaving.value) return
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/jpeg,image/png,image/webp,image/gif'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    imageSaving.value = true
    try {
      const url = await uploadImageForContent(file)
      const idx = paragraphIndex < 0 ? Math.max(0, chapterBlocks.value.filter((b) => b.type === 'text').length - 1) : paragraphIndex
      const baseContent = getAuthorChapterContent()
      const newContent = insertImageAfterParagraph(baseContent, idx, url)
      await saveChapterContent(newContent)
      notify('图片已插入', 'success')
    } catch (e) {
      handleError(e)
    } finally {
      imageSaving.value = false
    }
  }
  input.click()
}

async function onReplaceImage(afterParagraphIndex: number, oldUrl: string) {
  if (!isAuthorMode.value || !chapter.value || imageSaving.value) return
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/jpeg,image/png,image/webp,image/gif'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    imageSaving.value = true
    try {
      const url = await uploadImageForContent(file)
      let content = removeImageAt(getAuthorChapterContent(), afterParagraphIndex, oldUrl)
      content = insertImageAfterParagraph(content, afterParagraphIndex, url)
      await saveChapterContent(content)
      notify('图片已替换', 'success')
    } catch (e) {
      handleError(e)
    } finally {
      imageSaving.value = false
    }
  }
  input.click()
}

async function onRemoveImage(afterParagraphIndex: number, url: string) {
  if (!isAuthorMode.value || !chapter.value) return
  try {
    const newContent = removeImageAt(getAuthorChapterContent(), afterParagraphIndex, url)
    await saveChapterContent(newContent)
    notify('图片已删除', 'success')
  } catch (e) {
    handleError(e)
  }
}

async function onScrollChapterChange(id: number) {
  if (id === chapterId.value) {
    updateChapterMeta(id)
    await loadComments(id)
    return
  }
  scrollChainNavigating.value = true
  activeChapterId.value = id
  updateChapterMeta(id)
  await loadComments(id)
  flushProgress(true)
  router.replace(`/read/${bookId.value}/${id}`)
}

async function syncActiveChapter(id: number, reloadComments = true) {
  if (!isPageMode.value && scrollSections.value.some((s) => s.chapterId === id)) {
    if (id !== chapterId.value) {
      scrollChainNavigating.value = true
      router.replace(`/read/${bookId.value}/${id}`)
    }
    activeChapterId.value = id
    updateChapterMeta(id)
    if (reloadComments) await loadComments(id)
    return
  }
  switchChapter(id)
}

async function openParaComment(chId: number, index: number, mode: 'view' | 'compose') {
  await syncActiveChapter(chId)
  activeParaIndex.value = index
  if (mode === 'compose') newParaComment.value = ''
  chapterPanelOpen.value = false
  paraPanelOpen.value = true
  if (mode === 'compose') {
    nextTick(() => {
      paraCommentInput.value?.focus()
    })
  }
}

async function openChapterComment(chId: number, mode: 'view' | 'compose') {
  await syncActiveChapter(chId)
  activeChapterPanelId.value = chId
  if (mode === 'compose') newChapterComment.value = ''
  paraPanelOpen.value = false
  chapterPanelOpen.value = true
  if (mode === 'compose') {
    nextTick(() => {
      chapterCommentInput.value?.focus()
    })
  }
}

function focusChapterCommentInput() {
  const cid = Number(route.params.chapterId)
  openChapterComment(cid, 'compose')
}

function closeParaPanel() {
  paraPanelOpen.value = false
}

function closeChapterPanel() {
  chapterPanelOpen.value = false
}

async function submitParaComment() {
  const text = newParaComment.value.trim()
  if (!text) {
    notify('请输入段评内容')
    return
  }
  try {
    await submitParagraph(activeParaIndex.value, text)
    newParaComment.value = ''
  } catch (e) {
    handleError(e)
  }
}

async function submitChapterComment() {
  const content = newChapterComment.value.trim()
  if (!content) {
    notify('请输入章评内容')
    return
  }
  try {
    await submitChapter(content, undefined, activeChapterPanelId.value || progressChapterId.value)
    newChapterComment.value = ''
  } catch (e) {
    handleError(e)
  }
}

function onPinChapter(c: CommentItemType) {
  pinCommentItem(c, 'chapter')
}

function onDeleteChapter(c: CommentItemType) {
  removeComment(c, 'chapter')
}

async function onSubmitChapterReply(parent: CommentItemType, text: string) {
  try {
    await submitChapter(text, parent.id, activeChapterPanelId.value || progressChapterId.value)
  } catch (e) {
    handleError(e)
  }
}

function onPinParagraph(c: CommentItemType) {
  pinCommentItem(c, 'paragraph')
}

function onDeleteParagraph(c: CommentItemType) {
  removeComment(c, 'paragraph')
}

async function onSubmitParagraphReply(parent: CommentItemType, text: string) {
  try {
    await submitParagraph(activeParaIndex.value, text, parent.id)
  } catch (e) {
    handleError(e)
  }
}

let lastPageTurnAt = 0

function guardPageTurn(fn: () => void) {
  const now = Date.now()
  if (now - lastPageTurnAt < 350) return
  lastPageTurnAt = now
  fn()
}

function handlePrevPage() {
  guardPageTurn(() => {
    pageTurnDirection.value = 'backward'
    if (prevContentPage()) return
    const chapters = book.value?.chapters ?? []
    const idx = chapters.findIndex((c) => c.id === chapterId.value)
    if (idx > 0) {
      pendingPageOnChapterLoad.value = 'last'
      switchChapter(chapters[idx - 1].id)
    }
  })
}

function handleNextPage() {
  guardPageTurn(() => {
    pageTurnDirection.value = 'forward'
    if (currentPage.value < contentPageCount.value - 1) {
      currentPage.value += 1
      return
    }
    goNextChapter()
  })
}

function switchChapter(id: number) {
  flushProgress(true)
  panelOpen.value = false
  scrollChainNavigating.value = false
  router.replace(`/read/${book.value?.id}/${id}`)
}
</script>

<style scoped>
.reader {
  height: 100dvh;
  max-width: var(--reader-max-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: background 0.3s ease, color 0.3s ease;
}

.reader.theme-paper {
  background: #f7f6f2;
  color: #2a2a28;
}

.reader.theme-green {
  background: #e8efe4;
  color: #2a3328;
}

.reader.theme-night {
  background: #1a1d24;
  color: #d8d6d0;
}

.reader-toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: 12px;
  height: calc(52px + env(safe-area-inset-top, 0px));
  padding: env(safe-area-inset-top, 0px) 12px 0;
  background: color-mix(in srgb, var(--color-surface) 90%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border-soft);
  transform: translateY(-100%);
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.reader.toolbar-visible .reader-toolbar {
  transform: translateY(0);
}

.reader-toolbar.toolbar-editing {
  background: var(--color-accent-soft);
  border-bottom-color: var(--color-accent-muted);
}

.toolbar-edit-badge {
  display: inline-block;
  margin-right: 6px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 500;
  color: var(--color-accent);
  background: var(--color-surface);
  border-radius: var(--radius-full);
}

.toolbar-done-btn {
  width: auto;
  padding: 0 12px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-accent);
}

.toolbar-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: inherit;
}

.toolbar-btn:hover {
  background: var(--color-accent-soft);
}

.toolbar-title {
  flex: 1;
  min-width: 0;
  text-align: center;
}

.toolbar-book {
  display: block;
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toolbar-chapter {
  font-size: 12px;
  opacity: 0.65;
}

.reader-scroll-zone {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: calc(52px + env(safe-area-inset-top, 0px)) var(--reader-padding-x, 16px) calc(32px + env(safe-area-inset-bottom, 0px));
  -webkit-overflow-scrolling: touch;
}

.reader-scroll-zone.scroll-locked {
  overflow: hidden;
  touch-action: none;
}

.reader-content {
  font-family: inherit;
}

.reader-paragraph {
  content-visibility: auto;
  contain-intrinsic-size: auto 2.8em;
  margin-bottom: 1.2em;
  text-indent: 2em;
  cursor: default;
  user-select: text;
  position: relative;
}

.reader-chapter-section + .reader-chapter-section {
  margin-top: 2.5em;
  padding-top: 1.5em;
  border-top: 1px dashed color-mix(in srgb, currentColor 12%, transparent);
}

.reader-chapter-heading {
  font-family: var(--font-serif);
  font-size: 1.15em;
  font-weight: 600;
  margin: 0 0 1.2em;
  text-indent: 0;
}

.scroll-loading-hint {
  text-align: center;
  padding: 24px 0 8px;
  font-size: 13px;
  color: var(--color-text-muted);
}

.para-inline-mark {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: 6px;
  padding: 2px 8px;
  vertical-align: baseline;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-family: var(--font-sans);
  color: var(--color-accent);
  background: var(--color-accent-soft);
  text-indent: 0;
}

.reader-scroll-zone.page-mode {
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  padding-bottom: 12px;
}

.page-viewport {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.page-sheet {
  position: absolute;
  inset: 0;
  min-height: 0;
  overflow: hidden;
}

.page-tap-left,
.page-tap-right {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 28%;
  z-index: 10;
  touch-action: manipulation;
}

.page-tap-left {
  left: 0;
}

.page-tap-right {
  right: 0;
}

.reader-page-content {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 4px;
}

.page-slide-fwd-enter-active,
.page-slide-fwd-leave-active,
.page-slide-back-enter-active,
.page-slide-back-leave-active {
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.24s ease;
}

.page-slide-fwd-enter-from {
  transform: translateX(100%);
  opacity: 0.45;
}

.page-slide-fwd-leave-to {
  transform: translateX(-38%);
  opacity: 0.25;
}

.page-slide-back-enter-from {
  transform: translateX(-100%);
  opacity: 0.45;
}

.page-slide-back-leave-to {
  transform: translateX(38%);
  opacity: 0.25;
}

.page-indicator {
  text-align: center;
  font-size: 12px;
  color: var(--color-text-muted);
  padding: 6px 0 2px;
  flex-shrink: 0;
}

.chapter-panel-sub {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

/* 二级菜单 */
.reader-panel-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(20, 23, 30, 0.4);
  display: flex;
  align-items: flex-end;
}

@media (min-width: 768px) {
  .reader-panel-overlay {
    align-items: stretch;
    justify-content: flex-end;
  }
}

.reader-panel {
  width: 100%;
  max-height: 70dvh;
  background: var(--color-surface);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  will-change: transform;
}

@media (min-width: 768px) {
  .reader-panel {
    width: 360px;
    max-height: 100dvh;
    border-radius: 0;
  }
}

.reader-panel-enter-active,
.reader-panel-leave-active {
  transition: opacity 0.28s ease;
}

.reader-panel-enter-active .reader-panel,
.reader-panel-leave-active .reader-panel {
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
}

.reader-panel-enter-from,
.reader-panel-leave-to {
  opacity: 0;
}

.reader-panel-enter-from .reader-panel,
.reader-panel-leave-to .reader-panel {
  transform: translateY(100%);
}

@media (min-width: 768px) {
  .reader-panel-enter-from .reader-panel,
  .reader-panel-leave-to .reader-panel {
    transform: translateX(100%);
  }
}

.panel-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border-soft);
  flex-shrink: 0;
}

.panel-tab {
  flex: 1;
  padding: 14px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.panel-tab.active {
  color: var(--color-accent);
  font-weight: 500;
  box-shadow: inset 0 -2px 0 var(--color-accent);
}

.panel-body {
  padding: 20px;
  overflow-y: auto;
  overscroll-behavior: contain;
  flex: 1;
  min-height: 0;
}

.toc-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border-soft);
  font-size: 14px;
}

.toc-item.active {
  color: var(--color-accent);
  font-weight: 500;
}

.progress-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
  margin-top: 16px;
}

.progress-label:first-child {
  margin-top: 0;
}

.progress-chapter {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
}

.progress-bar {
  height: 6px;
  background: var(--color-border-soft);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-accent);
}

.progress-hint {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 8px 0;
}

.setting-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  background: var(--color-bg);
}

.mode-group,
.theme-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mode-btn {
  padding: 8px 14px;
  border-radius: var(--radius-full);
  font-size: 13px;
  border: 1px solid var(--color-border);
}

.mode-btn.active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.theme-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid transparent;
}

.theme-btn.active {
  border-color: var(--color-accent);
}

.setting-row {
  display: grid;
  grid-template-columns: 60px 1fr 48px;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 14px;
}

.setting-val {
  font-size: 12px;
  color: var(--color-text-muted);
  text-align: right;
}

.color-input {
  width: 40px;
  height: 32px;
  padding: 0;
  border: 1px solid var(--color-border-soft);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.custom-bg-row {
  grid-template-columns: 80px auto 48px;
}

/* 段评浮层 */
.para-panel-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(20, 23, 30, 0.45);
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

@media (min-width: 768px) {
  .para-panel-overlay {
    align-items: stretch;
    justify-content: flex-end;
  }
}

.para-panel {
  width: 100%;
  max-height: 85dvh;
  background: var(--color-surface);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  will-change: transform;
}

@media (min-width: 768px) {
  .para-panel {
    width: min(100%, 360px);
    height: 100%;
    max-height: 100%;
    border-radius: 0;
  }
}

.para-overlay-enter-active,
.para-overlay-leave-active {
  transition: opacity 0.28s ease;
}

.para-overlay-enter-active .para-panel,
.para-overlay-leave-active .para-panel {
  transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
}

.para-overlay-enter-from,
.para-overlay-leave-to {
  opacity: 0;
}

.para-overlay-enter-from .para-panel,
.para-overlay-leave-to .para-panel {
  transform: translateY(100%);
}

@media (min-width: 768px) {
  .para-overlay-enter-from .para-panel,
  .para-overlay-leave-to .para-panel {
    transform: translateX(100%);
  }
}

.para-panel-head {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border-soft);
  font-weight: 500;
}

.para-preview {
  flex-shrink: 0;
  margin: 12px 16px 0;
  font-size: 13px;
  color: var(--color-text-secondary);
  padding: 12px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  line-height: 1.6;
  max-height: 88px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.para-panel-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 12px 16px;
  -webkit-overflow-scrolling: touch;
}

.para-panel-compose {
  flex-shrink: 0;
  padding: 12px 16px 16px;
  border-top: 1px solid var(--color-border-soft);
  background: var(--color-bg-elevated);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.para-comment {
  font-size: 14px;
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--color-border-soft);
}

.para-comment p {
  margin-top: 4px;
  color: var(--color-text-secondary);
}

.para-empty-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  text-align: center;
  padding: 24px 0;
}
</style>
