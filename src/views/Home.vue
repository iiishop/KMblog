<script setup>
import SelfIntroduction from '@/components/SelfIntroduction.vue';
import HeadMenu from '@/components/HeadMenu.vue';
import TagPanel from '@/components/TagPanel.vue';
import CollectionPanel from '@/components/CollectionPanel.vue';
import PostPanel from '@/components/PostPanel.vue';

</script>

<template>
  <HeadMenu />
  <div class="Scene">
    <PostPanel />
    <div class="RightList">
      <SelfIntroduction />
      <CollectionPanel />
      <TagPanel />
    </div>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Noto Sans SC', sans-serif;
  background: var(--body-background-color);
  color: var(--body-text-color);
  overflow: auto;
}

.Scene {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 2rem;
  padding-top: 6rem;
}

.RightList {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
  width: 25rem;
  color: var(--rightlist-text-color);
}
</style>