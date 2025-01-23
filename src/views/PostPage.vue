<script setup>
import { defineProps, defineAsyncComponent } from 'vue';

// 使用 Vite 的代码分割功能进行动态导入
const BaseLayout = defineAsyncComponent(() => import('@/views/BaseLayout.vue'));
const MarkdownPanel = defineAsyncComponent(() => import('@/components/MarkdownPanel.vue'));

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