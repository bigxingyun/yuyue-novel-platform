<template>

  <p

    class="reader-paragraph"

    @dblclick="$emit('dblclick', paragraphIndex)"

    @touchstart.passive="$emit('touchstart', $event)"

    @touchend="$emit('touchend', $event)"

    @click.stop

  >

    {{ text }}<button

      v-if="!hideComments && (commentCount ?? 0) > 0"

      type="button"

      class="para-inline-mark"

      :aria-label="`${commentCount} 条段评`"

      @click.stop="$emit('openComments')"

    >

      <PhChatCircle :size="13" weight="fill" />

      <span>{{ commentCount }}</span>

    </button>

  </p>

</template>



<script setup lang="ts">

import { PhChatCircle } from '@phosphor-icons/vue'



defineProps<{

  text: string

  paragraphIndex: number

  commentCount?: number

  hideComments?: boolean

}>()



defineEmits<{

  dblclick: [paragraphIndex: number]

  touchstart: [event: TouchEvent]

  touchend: [event: TouchEvent]

  openComments: []

}>()

</script>



<style scoped>

.reader-paragraph {

  margin: 0 0 1.2em;

  text-indent: 2em;

  content-visibility: auto;

  contain-intrinsic-size: auto 3em;

}



.para-inline-mark {

  display: inline-flex;

  align-items: center;

  gap: 2px;

  margin-left: 4px;

  padding: 2px 6px;

  vertical-align: middle;

  border-radius: var(--radius-full);

  font-size: 11px;

  color: var(--color-accent);

  background: var(--color-accent-soft);

}

</style>

