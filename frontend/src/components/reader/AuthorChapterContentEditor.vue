<template>
  <div class="author-chapter-content-editor">
    <template v-for="(block, index) in blocks" :key="blockKey(block, index)">
      <ReaderParagraph
        v-if="block.type === 'text'"
        :text="block.text"
        :paragraph-index="block.paragraphIndex"
        :comment-count="0"
        :hide-comments="true"
      />
      <AuthorImageBlockChrome
        v-else
        :url="block.url"
        :edit-mode="true"
        @remove="$emit('removeImage', block.afterParagraphIndex, block.url)"
        @replace="$emit('replaceImage', block.afterParagraphIndex, block.url)"
      />
      <AuthorBlockInsertBar
        v-if="block.type === 'text'"
        @insert="$emit('insertImage', block.paragraphIndex)"
      />
    </template>
    <AuthorBlockInsertBar
      v-if="blocks.length === 0"
      @insert="$emit('insertImage', -1)"
    />
  </div>
</template>

<script setup lang="ts">
import AuthorBlockInsertBar from '@/components/reader/AuthorBlockInsertBar.vue'
import AuthorImageBlockChrome from '@/components/reader/AuthorImageBlockChrome.vue'
import ReaderParagraph from '@/components/reader/ReaderParagraph.vue'
import type { ChapterBlock } from '@/types/chapterBlock'

defineProps<{
  blocks: ChapterBlock[]
}>()

defineEmits<{
  insertImage: [paragraphIndex: number]
  removeImage: [afterParagraphIndex: number, url: string]
  replaceImage: [afterParagraphIndex: number, url: string]
}>()

function blockKey(block: ChapterBlock, index: number) {
  if (block.type === 'text') return `t-${block.paragraphIndex}-${index}`
  return `i-${block.afterParagraphIndex}-${block.url}`
}
</script>

<style scoped>
.author-chapter-content-editor {
  width: 100%;
}
</style>
