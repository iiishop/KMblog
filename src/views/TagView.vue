<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import TagPanel from '@/components/TagPanel.vue';
</script>

<template>
  <BaseLayout :showTipList="false">
    <template #main>
      <TagPanel />
    </template>
  </BaseLayout>
</template>