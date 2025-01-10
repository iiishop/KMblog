<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import PostPanel from '@/components/PostPanel.vue';
</script>

<template>
  <BaseLayout>
    <template #middle>
      <PostPanel />
    </template>
  </BaseLayout>
</template>