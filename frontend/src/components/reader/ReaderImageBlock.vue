<template>

  <figure class="reader-image-block">

    <img :src="displayUrl" :alt="alt" loading="lazy" @click.stop @load="$emit('loaded')" />

  </figure>

</template>



<script setup lang="ts">

import { computed } from 'vue'

import { resolveMediaUrl } from '@/utils/mediaUrl'



const props = withDefaults(

  defineProps<{

    url: string

    alt?: string

  }>(),

  { alt: '章节插图' },

)



const displayUrl = computed(() => resolveMediaUrl(props.url))

defineEmits<{ loaded: [] }>()

</script>



<style scoped>

.reader-image-block {

  margin: 0.6em 0 1.4em;

  padding: 0;

  text-align: center;

}



.reader-image-block img {

  display: block;

  width: 100%;

  max-width: 100%;

  max-height: min(70vh, 520px);

  margin: 0 auto;

  object-fit: contain;

  border-radius: var(--radius-md);

  box-shadow: var(--shadow-sm);

}

</style>

