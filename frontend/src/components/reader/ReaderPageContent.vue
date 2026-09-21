<template>
  <template v-for="slice in slices" :key="sliceKey(slice)">
    <ReaderChapterCommentCard
      v-if="slice.isChapterComment"
      :featured="featuredChapterComment"
      :count="chapterCommentCount"
      @open="$emit('openChapterComment', chapterCommentMode)"
    />
    <ReaderImageBlock v-else-if="slice.isImage && slice.imageUrl" :url="slice.imageUrl" @loaded="$emit('imageLoaded')" />
    <ReaderParagraph
      v-else
      :text="slice.text"
      :paragraph-index="slice.paraIndex"
      :comment-count="paraCommentCount(chapterId, slice.paraIndex)"
      @dblclick="$emit('paraDblClick', chapterId, slice.paraIndex)"
      @touchstart="$emit('paraTouchStart', chapterId, slice.paraIndex, $event)"
      @touchend="$emit('paraTouchEnd', chapterId, slice.paraIndex, $event)"
      @open-comments="$emit('openParaComment', chapterId, slice.paraIndex, 'view')"
    />
  </template>
</template>

<script setup lang="ts">
import ReaderChapterCommentCard from '@/components/reader/ReaderChapterCommentCard.vue'
import ReaderImageBlock from '@/components/reader/ReaderImageBlock.vue'
import ReaderParagraph from '@/components/reader/ReaderParagraph.vue'
import type { PageSlice } from '@/composables/useReaderPagination'
import type { CommentItem } from '@/types/comment'

defineProps<{
  slices: PageSlice[]
  chapterId: number
  paraCommentCount: (chapterId: number, paraIndex: number) => number
  featuredChapterComment: CommentItem | null
  chapterCommentCount: number
  chapterCommentMode: 'view' | 'compose'
}>()

defineEmits<{
  paraDblClick: [chapterId: number, paraIndex: number]
  paraTouchStart: [chapterId: number, paraIndex: number, event: TouchEvent]
  paraTouchEnd: [chapterId: number, paraIndex: number, event: TouchEvent]
  openParaComment: [chapterId: number, paraIndex: number, mode: 'view' | 'compose']
  openChapterComment: [mode: 'view' | 'compose']
  imageLoaded: []
}>()

function sliceKey(slice: PageSlice) {
  if (slice.isChapterComment) return 'chapter-comment'
  if (slice.isImage) return `img-${slice.afterParagraphIndex}-${slice.imageUrl}`
  return `p-${slice.paraIndex}-${slice.text.slice(0, 24)}`
}
</script>
