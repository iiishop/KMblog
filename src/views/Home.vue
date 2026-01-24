<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import PostPanel from '@/components/PostPanel.vue';
import AnnouncementPanel from '@/components/AnnouncementPanel.vue';
</script>

<template>
  <BaseLayout :showTipList="false">
    <template #main>
      <AnnouncementPanel />
      <PostPanel />
    </template>
  </BaseLayout>
</template>