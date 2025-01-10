<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import PostPanel from '@/components/PostPanel.vue';
</script>

<template>
  <BaseLayout :showTipList="false">
    <template #main>
      <PostPanel />
    </template>
  </BaseLayout>
</template>