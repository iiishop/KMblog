<script setup>
import { defineAsyncComponent } from 'vue';

// 使用 Vite 的代码分割功能进行动态导入
const BaseLayout = defineAsyncComponent(() => import('@/views/BaseLayout.vue'));
const TagPanel = defineAsyncComponent(() => import('@/components/TagPanel.vue'));
</script>

<template>
  <BaseLayout :showTipList="false">
    <template #main>
      <TagPanel />
    </template>
  </BaseLayout>
</template>