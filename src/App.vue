<script setup>
import { ref } from 'vue';
import PostPanel from './components/PostPanel.vue';
import SelfIntroduction from './components/SelfIntroduction.vue';

// 数据数组，每个对象包含 imageUrl 和 markdownUrl
const posts = ref([
  { imageUrl: '/src/Posts/Images/1.jpg', markdownUrl: '/src/Posts/Markdowns/1.md' },
  { imageUrl: '/src/Posts/Images/1.jpg', markdownUrl: '/src/Posts/Markdowns/1.md' },
  { imageUrl: '/src/Posts/Images/1.jpg', markdownUrl: '/src/Posts/Markdowns/1.md' },
]);
</script>

<template>
  <div class="Scene">

    <div class="Posts">
      <!-- 使用 v-for 指令迭代 posts 数组 -->
      <PostPanel v-for="(post, index) in posts" :key="index" :imageUrl="post.imageUrl"
        :markdownUrl="post.markdownUrl" />
    </div>
    <div class="RightList">
      <SelfIntroduction />
    </div>
  </div>
</template>

<style>
.Scene {
  margin: 0;
  padding: 0;
  font-family: 'Noto Sans SC', sans-serif;
  background: white;
  display: flex;
  flex-direction: row;
  width: 100vw;
  justify-content: center;
  align-items: center;
  gap: 2rem;
}

.Posts {
  display: flex;
  gap: 2rem;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 50vw;
}
</style>