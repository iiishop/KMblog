<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import MarkdownPanel from '@/components/MarkdownPanel.vue';
</script>

<template>
  <BaseLayout :showTipList="false">
    <template #main>
      <MarkdownPanel :markdown-url="'/src/Posts/Markdowns/1.md'" />
    </template>
  </BaseLayout>
</template>