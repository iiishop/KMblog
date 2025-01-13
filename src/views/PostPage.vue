<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import MarkdownPanel from '@/components/MarkdownPanel.vue';

const props = defineProps({
  markdownUrl: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <BaseLayout :showTipList="false">
    <template #main>
      <MarkdownPanel :markdown-url="props.markdownUrl" />
    </template>
  </BaseLayout>
</template>