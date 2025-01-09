<script setup>
import { onMounted, ref } from 'vue';
import globalVar from './globalVar';
import config from './config';
import PostPanel from './components/PostPanel.vue';
import SelfIntroduction from './components/SelfIntroduction.vue';
import HeadMenu from './components/HeadMenu.vue';
import TagPanel from './components/TagPanel.vue';
import CollectionPanel from './components/CollectionPanel.vue';
import './color.css'; // 导入 color.css

// 数据数组，每个对象包含 imageUrl 和 markdownUrl
const posts = ref([]);

// 设置主题
const setTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
};

onMounted(() => {
  posts.value = globalVar.markdowns;

  document.title = config.BlogName + "|" + config.ShortDesc;

  // 应用主题
  setTheme(config.theme);
});
</script>

<template>
  <HeadMenu />
  <div class="Scene">
    <div class="Posts">
      <!-- 使用 v-for 指令迭代 posts 数组 -->
      <PostPanel v-for="(post, index) in posts" :key="post.id" :imageUrl="post.imageUrl"
        :markdownUrl="post.markdownUrl" />
    </div>
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

.Posts {
  display: flex;
  gap: 2rem;
  flex-direction: column;
  width: 50vw;
  color: var(--posts-text-color);
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