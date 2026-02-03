<script setup>
import HeroSection from '@/components/HeroSection.vue';
import BaseLayout from '@/views/BaseLayout.vue';
import PostPanel from '@/components/PostPanel.vue';
import AnnouncementPanel from '@/components/AnnouncementPanel.vue';
</script>

<template>
  <div class="home-page">
    <HeroSection />
    <BaseLayout :showTipList="false">
      <template #main>
        <AnnouncementPanel />
        <PostPanel />
      </template>
    </BaseLayout>
  </div>
</template>

<style scoped>
.home-page {
  width: 100%;
}
</style>