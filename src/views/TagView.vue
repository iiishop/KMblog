<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import TagPanel from '@/components/TagPanel.vue';
</script>

<template>
  <BaseLayout>
    <template #middle>
      <TagPanel />
    </template>
  </BaseLayout>
</template>