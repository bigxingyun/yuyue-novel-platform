<template>
  <template v-for="(block, index) in blocks" :key="blockKey(block, index)">
    <ReaderParagraph
      v-if="block.type === 'text'"
      :text="block.text"
      :paragraph-index="block.paragraphIndex"
      :comment-count="paraCommentCount(chapterId, block.paragraphIndex)"
      @dblclick="$emit('paraDblClick', chapterId, block.paragraphIndex)"
      @touchstart="$emit('paraTouchStart', chapterId, block.paragraphIndex, $event)"
      @touchend="$emit('paraTouchEnd', chapterId, block.paragraphIndex, $event)"
      @open-comments="$emit('openParaComment', chapterId, block.paragraphIndex, 'view')"
    />
    <ReaderImageBlock v-else :url="block.url" />
  </template>
</template>

<script setup lang="ts">
import ReaderImageBlock from '@/components/reader/ReaderImageBlock.vue'
import ReaderParagraph from '@/components/reader/ReaderParagraph.vue'
import type { ChapterBlock } from '@/types/chapterBlock'

defineProps<{
  blocks: ChapterBlock[]
  chapterId: number
  paraCommentCount: (chapterId: number, paraIndex: number) => number
}>()

defineEmits<{
  paraDblClick: [chapterId: number, paraIndex: number]
  paraTouchStart: [chapterId: number, paraIndex: number, event: TouchEvent]
  paraTouchEnd: [chapterId: number, paraIndex: number, event: TouchEvent]
  openParaComment: [chapterId: number, paraIndex: number, mode: 'view' | 'compose']
}>()

function blockKey(block: ChapterBlock, index: number) {
  if (block.type === 'text') return `t-${block.paragraphIndex}-${index}`
  return `i-${block.afterParagraphIndex}-${block.url}`
}
</script>
